from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def handler404(_request, _exception=None):
    return JsonResponse({'detail': 'Not found.'}, status=404)


def handler500(_request):
    return JsonResponse({'detail': 'Internal server error.'}, status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls')),
    path('', include('apps.converter.urls')),
    path('', include('apps.history.urls')),
]
