from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'action', 'resource', 'resource_id', 'user', 'ip_address']
    list_filter = ['action', 'resource']
    search_fields = ['description', 'resource_id']
    readonly_fields = ['user', 'action', 'resource', 'resource_id', 'description',
                       'ip_address', 'checksum', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
