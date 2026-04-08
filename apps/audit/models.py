from django.db import models
from django.conf import settings
from utils.crypto import sha256

ACTION_CHOICES = [
    ('CREATE', 'Create'),
    ('UPDATE', 'Update'),
    ('DELETE', 'Delete'),
    ('LOGIN', 'Login'),
    ('ACCESS', 'Access'),
    ('ERROR', 'Error'),
]


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    checksum = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Audit logs'

    def save(self, *args, **kwargs):
        content = f"{self.user_id}{self.action}{self.resource}{self.resource_id or ''}{self.description}"
        self.checksum = sha256(content)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.action}] {self.resource}({self.resource_id}) by user {self.user_id}"
