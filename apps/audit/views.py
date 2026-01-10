"""Views for Audit Log API."""
from rest_framework import viewsets, permissions
from django_filters import rest_framework as filters
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogFilter(filters.FilterSet):
    """Filter for audit log queries."""
    model_name = filters.CharFilter()
    action = filters.ChoiceFilter(choices=AuditLog.Action.choices)
    user = filters.NumberFilter()
    date_from = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = AuditLog
        fields = ['model_name', 'action', 'user', 'object_id']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for audit logs."""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AuditLogFilter
    ordering_fields = ['timestamp']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Non-admin users can only see their own logs
        if not self.request.user.is_admin:
            queryset = queryset.filter(user=self.request.user)

        return queryset.select_related('user')