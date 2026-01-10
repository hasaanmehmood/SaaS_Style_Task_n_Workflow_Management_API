"""Custom permissions for project access control."""
from rest_framework import permissions
from .models import ProjectMember


class IsProjectMember(permissions.BasePermission):
    """Permission to check if user is a project member."""

    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_admin:
            return True

        # Get project from object
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj

        # Check if user is project owner or member
        if project.owner == request.user:
            return True

        return ProjectMember.objects.filter(
            project=project,
            user=request.user
        ).exists()


class IsProjectAdmin(permissions.BasePermission):
    """Permission to check if user is a project admin."""

    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_admin:
            return True

        # Get project from object
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj

        # Check if user is project owner
        if project.owner == request.user:
            return True

        # Check if user is project admin
        try:
            member = ProjectMember.objects.get(project=project, user=request.user)
            return member.role == ProjectMember.Role.ADMIN
        except ProjectMember.DoesNotExist:
            return False