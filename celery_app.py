# =============================================================================
# FILE: celery_app.py  (project root)
# SPRINT 7 UPDATE: Added abandoned-delivery cleanup + expired-sharelink cleanup.
# All Sprint 4, 5, 6 schedules preserved exactly.
# =============================================================================
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('edms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # ---- Sprint 4 (preserved) -------------------------------------------
    'purge-expired-notifications': {
        'task':     'notifications.purge_expired',
        'schedule': crontab(hour=20, minute=30),
    },
    'purge-old-read-notifications': {
        'task':     'notifications.purge_old_read',
        'schedule': crontab(hour=21, minute=30, day_of_week=0),
    },
    'overdue-work-reminders': {
        'task':     'notifications.overdue_work_reminders',
        'schedule': crontab(hour=2, minute=30),
    },
    'approval-sla-reminders': {
        'task':     'notifications.approval_sla_reminders',
        'schedule': crontab(hour=3, minute=30),
    },
    # ---- Sprint 5 (preserved) -------------------------------------------
    'ml-retrain-weekly': {
        'task':     'ml.retrain_all',
        'schedule': crontab(hour=19, minute=30, day_of_week=0),
        'kwargs':   {'user_id': None},
    },
    # ---- Sprint 6 (preserved) -------------------------------------------
    'sanity-check-weekly': {
        'task':     'sanity.run_checks',
        'schedule': crontab(hour=1, minute=30, day_of_week=1),
        'kwargs':   {'stale_draft_days': 90},
    },
    # ---- Sprint 7 -------------------------------------------------------
    # Purge expired share links daily at 00:30 IST (19:00 UTC previous day)
    'purge-expired-sharelinks': {
        'task':     'sharelinks.purge_expired',
        'schedule': crontab(hour=19, minute=0),
    },
    # Purge ABANDONED webhook deliveries older than 30 days, weekly
    'purge-old-webhook-deliveries': {
        'task':     'webhooks.purge_old_deliveries',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),
        'kwargs':   {'days': 30},
    },
}
