"""Signal handlers for audit logging."""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
import json

from .models import AuditLog
from apps.tasks.models import Task, Comment
from apps.projects.models import Project, Board, ProjectMember

AUDITED_MODELS = [Task, Comment, Project, Board, ProjectMember]


def get_model_changes(instance, created=False):
    """Extract changes from model instance."""
    if created:
        return {
            field.name: str(getattr(instance, field.name))
            for field in instance._meta.fields
            if field.name not in ['password']
        }
    else:
        return {'updated': True}


@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    """Log create and update actions."""
    if sender not in AUDITED_MODELS:
        return

    request = getattr(instance, '_request', None)
    user = getattr(request, '_audit_user', None) if request else None
    ip_address = getattr(request, '_audit_ip', None) if request else None
    user_agent = getattr(request, '_audit_user_agent', '') if request else ''

    if not user:
        return

    action = AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE
    changes = get_model_changes(instance, created)

    try:
        json_changes = json.loads(json.dumps(changes, cls=DjangoJSONEncoder))
    except (TypeError, ValueError):
        json_changes = {'error': 'Unable to serialize changes'}

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=sender.__name__,
        object_id=instance.pk,
        changes=json_changes,
        ip_address=ip_address,
        user_agent=user_agent
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Log delete actions."""
    if sender not in AUDITED_MODELS:
        return

    request = getattr(instance, '_request', None)
    user = getattr(request, '_audit_user', None) if request else None
    ip_address = getattr(request, '_audit_ip', None) if request else None
    user_agent = getattr(request, '_audit_user_agent', '') if request else ''

    if not user:
        return

    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.DELETE,
        model_name=sender.__name__,
        object_id=instance.pk,
        changes={'deleted': True},
        ip_address=ip_address,
        user_agent=user_agent
    )