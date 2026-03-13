# =============================================================================
# FILE: celery_app.py  (project root)
# SPRINT 4 — Celery application + Beat schedule
# Start worker : celery -A celery_app worker -l info -P solo   (LAN / Windows)
# Start beat   : celery -A celery_app beat   -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
# Broker       : Redis on localhost:6379/0  (or RabbitMQ — change BROKER_URL)
# No external internet required — Redis runs on the same LAN server as Django.
# =============================================================================
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('edms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ---------------------------------------------------------------------------
# Beat schedule — all times IST (UTC+5:30 → subtract 5:30 for UTC crontab)
# ---------------------------------------------------------------------------
app.conf.beat_schedule = {
    # Purge expired notifications daily at 02:00 IST (20:30 UTC previous day)
    'purge-expired-notifications': {
        'task':     'notifications.purge_expired',
        'schedule': crontab(hour=20, minute=30),
    },

    # Purge old read notifications every Sunday at 03:00 IST (21:30 UTC Saturday)
    'purge-old-read-notifications': {
        'task':     'notifications.purge_old_read',
        'schedule': crontab(hour=21, minute=30, day_of_week=0),
    },

    # Overdue work reminders daily at 08:00 IST (02:30 UTC)
    'overdue-work-reminders': {
        'task':     'notifications.overdue_work_reminders',
        'schedule': crontab(hour=2, minute=30),
    },

    # Approval SLA reminders daily at 09:00 IST (03:30 UTC)
    'approval-sla-reminders': {
        'task':     'notifications.approval_sla_reminders',
        'schedule': crontab(hour=3, minute=30),
    },
}
