import json
import logging
from django.http import JsonResponse
from utils.crypto import encrypt_aes256, decrypt_aes256
from utils.request_context import set_current_ip

SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
}

request_logger = logging.getLogger('converter.requests')
error_logger = logging.getLogger('converter.errors')

_SKIP_PREFIXES = ('/admin/', '/static/', '/media/')


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(request.path.startswith(p) for p in _SKIP_PREFIXES):
            return self.get_response(request)

        ip = _get_client_ip(request)
        set_current_ip(ip)
        user_id = getattr(getattr(request, 'user', None), 'id', 'anon')
        request_logger.info(f"{request.method} {request.path} user={user_id} ip={ip}")

        response = self.get_response(request)
        request_logger.info(f"{request.method} {request.path} → {response.status_code}")
        return response


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for header, value in SECURITY_HEADERS.items():
            response[header] = value
        return response


class AESEncryptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.headers.get('X-Encrypted') != 'true':
            return self.get_response(request)

        try:
            body = request.body.decode('utf-8')
            decrypted = decrypt_aes256(body)
            request._body = decrypted.encode('utf-8')
            request.META['CONTENT_TYPE'] = 'application/json'
        except Exception as exc:
            error_logger.error(f"AES decryption failed: {exc}", exc_info=True)
            return JsonResponse({'error': 'Decryption failed'}, status=400)

        response = self.get_response(request)

        try:
            content = response.content.decode('utf-8')
            encrypted = encrypt_aes256(content)
            response.content = json.dumps({'data': encrypted}).encode('utf-8')
            response['Content-Type'] = 'application/json'
            response['X-Encrypted'] = 'true'
        except Exception as exc:
            error_logger.error(f"AES response encryption failed: {exc}", exc_info=True)

        return response
