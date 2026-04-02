import hashlib
import os
import base64
from django.conf import settings
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def _get_key() -> bytes:
    return bytes.fromhex(settings.AES_SECRET_KEY)


def encrypt_aes256(plaintext: str) -> str:
    nonce = os.urandom(12)
    aesgcm = AESGCM(_get_key())
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(nonce + ciphertext).decode('utf-8')


def decrypt_aes256(encrypted: str) -> str:
    data = base64.b64decode(encrypted)
    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(_get_key())
    return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
