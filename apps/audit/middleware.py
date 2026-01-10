"""Middleware for audit logging."""
from .models import AuditLog


class AuditMiddleware:
    """Middleware to capture audit information."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request info for signal handlers
        if hasattr(request, 'user') and request.user.is_authenticated:
            request._audit_user = request.user
            request._audit_ip = self.get_client_ip(request)
            request._audit_user_agent = request.META.get('HTTP_USER_AGENT', '')

        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip