"""Serializers for Audit Log API."""
from rest_framework import serializers
from .models import AuditLog
from apps.users.serializers import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs."""
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_detail', 'action', 'model_name',
            'object_id', 'changes', 'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = fields