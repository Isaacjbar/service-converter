from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'

    def ready(self):
        import apps.audit.signals  # noqa: F401
        from apps.audit.signals import connect_user_signals
        connect_user_signals()
