"""Task models."""
from django.db import models
from django.conf import settings
from apps.projects.models import Board


class Task(models.Model):
    """Task model with lifecycle management."""

    class Status(models.TextChoices):
        BACKLOG = 'BACKLOG', 'Backlog'
        TODO = 'TODO', 'To Do'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        REVIEW = 'REVIEW', 'In Review'
        DONE = 'DONE', 'Done'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BACKLOG
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_tasks'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    sla_breached = models.BooleanField(default=False)
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['board', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Set completed_at when status changes to DONE
        if self.status == self.Status.DONE and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif self.status != self.Status.DONE:
            self.completed_at = None

        super().save(*args, **kwargs)


class Comment(models.Model):
    """Comment model for task discussions."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author.email} on {self.task.title}"