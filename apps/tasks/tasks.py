"""Celery tasks for async operations."""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_task_assignment_email(task_id, user_id):
    """Send email when task is assigned."""
    from .models import Task
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        task = Task.objects.select_related('board__project', 'reporter').get(id=task_id)
        user = User.objects.get(id=user_id)

        subject = f'New Task Assigned: {task.title}'
        message = f"""
        Hello {user.get_full_name() or user.username},

        You have been assigned a new task:

        Task: {task.title}
        Project: {task.board.project.name}
        Board: {task.board.name}
        Priority: {task.get_priority_display()}
        Reporter: {task.reporter.get_full_name() or task.reporter.username}

        {'Due Date: ' + task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else ''}

        Description:
        {task.description}

        Please check the task management system for more details.
        """

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Task assignment email sent to {user.email} for task {task_id}")

    except Exception as e:
        logger.error(f"Failed to send task assignment email: {str(e)}")


@shared_task
def check_sla_breaches():
    """Check for overdue tasks and mark SLA breaches."""
    from .models import Task

    now = timezone.now()
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        status__in=[Task.Status.BACKLOG, Task.Status.TODO, Task.Status.IN_PROGRESS],
        sla_breached=False
    )

    count = overdue_tasks.update(sla_breached=True)
    logger.info(f"Marked {count} tasks as SLA breached")

    return count


@shared_task
def send_daily_task_summary():
    """Send daily task summary to users."""
    from .models import Task
    from django.contrib.auth import get_user_model

    User = get_user_model()

    for user in User.objects.filter(is_active=True):
        # Get user's tasks
        tasks = Task.objects.filter(
            assignee=user,
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
        ).select_related('board__project')

        if not tasks.exists():
            continue

        # Categorize tasks
        overdue = tasks.filter(due_date__lt=timezone.now())
        due_today = tasks.filter(
            due_date__date=timezone.now().date()
        )
        high_priority = tasks.filter(priority__in=[Task.Priority.HIGH, Task.Priority.CRITICAL])

        subject = f'Daily Task Summary - {timezone.now().strftime("%Y-%m-%d")}'
        message = f"""
        Hello {user.get_full_name() or user.username},

        Here's your daily task summary:

        Total Active Tasks: {tasks.count()}
        Overdue Tasks: {overdue.count()}
        Due Today: {due_today.count()}
        High Priority: {high_priority.count()}

        {'Overdue Tasks:' if overdue.exists() else ''}
        {chr(10).join([f"- {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})" for task in overdue[:5]])}

        Please review and update your tasks in the system.
        """

        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"Daily summary sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send daily summary to {user.email}: {str(e)}")


@shared_task
def send_webhook_notification(task_id, event_type):
    """Send webhook notification for task events."""
    import requests
    from .models import Task

    try:
        task = Task.objects.select_related('board__project', 'assignee', 'reporter').get(id=task_id)

        # This is a placeholder - in production, you'd have webhook URLs configured per project
        webhook_url = "https://your-webhook-endpoint.com/notifications"

        payload = {
            'event': event_type,
            'task': {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'assignee': task.assignee.email if task.assignee else None,
                'project': task.board.project.name,
            },
            'timestamp': timezone.now().isoformat()
        }

        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()

        logger.info(f"Webhook sent for task {task_id}: {event_type}")

    except Exception as e:
        logger.error(f"Failed to send webhook for task {task_id}: {str(e)}")