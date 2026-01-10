"""Project and Board models."""
from django.db import models
from django.conf import settings


class Project(models.Model):
    """Project model representing a workspace."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_archived']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    """Project membership with role."""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        MEMBER = 'MEMBER', 'Member'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_members'
        unique_together = ['project', 'user']
        indexes = [
            models.Index(fields=['project', 'user']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.project.name} ({self.role})"


class Board(models.Model):
    """Board model for organizing tasks."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='boards'
    )
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'boards'
        ordering = ['position', 'created_at']
        indexes = [
            models.Index(fields=['project', 'position']),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.name}"