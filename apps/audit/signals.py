import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.history.models import DiagramHistory
from apps.audit.models import AuditLog
from utils.request_context import get_current_ip

logger = logging.getLogger('converter.errors')


def _write_log(user, action, resource, resource_id, description):
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id else '',
            description=description,
            ip_address=get_current_ip(),
        )
    except Exception as exc:
        logger.error(f"AuditLog write failed: {exc}", exc_info=True)


@receiver(post_save, sender=DiagramHistory)
def on_diagram_history_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    _write_log(
        instance.user, action, 'DiagramHistory', instance.id,
        f"file={instance.filename} version={instance.version}"
    )


@receiver(post_delete, sender=DiagramHistory)
def on_diagram_history_delete(sender, instance, **kwargs):
    _write_log(
        instance.user, 'DELETE', 'DiagramHistory', instance.id,
        f"file={instance.filename} version={instance.version}"
    )


def connect_user_signals():
    user_model = get_user_model()

    @receiver(post_save, sender=user_model)
    def on_user_save(sender, instance, created, **kwargs):
        action = 'CREATE' if created else 'UPDATE'
        _write_log(
            None, action, 'User', instance.id,
            f"username={instance.username} email={instance.email}"
        )

    @receiver(post_delete, sender=user_model)
    def on_user_delete(sender, instance, **kwargs):
        _write_log(
            None, 'DELETE', 'User', instance.id,
            f"username={instance.username} email={instance.email}"
        )
