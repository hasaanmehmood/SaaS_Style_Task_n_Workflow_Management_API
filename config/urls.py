"""URL configuration for Task Management API."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# API Documentation Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Task Management API",
        default_version='v1',
        description="Production-grade SaaS task management system",
        contact=openapi.Contact(email="api@taskmanager.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring."""
    from django.db import connection
    from django.core.cache import cache

    health_status = {
        'status': 'healthy',
        'database': 'connected',
        'cache': 'connected',
    }

    # Check database
    try:
        connection.ensure_connection()
    except Exception:
        health_status['database'] = 'disconnected'
        health_status['status'] = 'unhealthy'

    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
    except Exception:
        health_status['cache'] = 'disconnected'
        health_status['status'] = 'unhealthy'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return Response(health_status, status=status_code)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),

    # API v1 endpoints
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)