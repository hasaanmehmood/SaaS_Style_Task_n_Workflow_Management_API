"""URL configuration for Project API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, BoardViewSet

router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = router.urls