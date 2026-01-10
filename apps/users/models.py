"""User models for Task Management API."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based permissions."""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        MEMBER = 'MEMBER', 'Member'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_manager(self):
        return self.role in [self.Role.ADMIN, self.Role.MANAGER]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username