"""Audit log models for tracking changes."""
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Audit log for tracking all changes."""

    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]

    def __str__(self):
        return f"{self.action} {self.model_name} by {self.user} at {self.timestamp}"