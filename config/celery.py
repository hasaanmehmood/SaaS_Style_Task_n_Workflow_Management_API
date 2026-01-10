"""Celery configuration for Task Management API."""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'check-sla-breaches-every-hour': {
        'task': 'apps.tasks.tasks.check_sla_breaches',
        'schedule': crontab(minute=0),  # Every hour
    },
    'send-daily-summary': {
        'task': 'apps.tasks.tasks.send_daily_task_summary',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')