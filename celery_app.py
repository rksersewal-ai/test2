# =============================================================================
# FILE: celery_app.py  (project root)
# SPRINT 6 UPDATE: Added sanity check weekly schedule.
# All Sprint 4 + 5 schedules preserved exactly.
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
    # ---- Sprint 6 -------------------------------------------------------
    # Sanity check every Monday at 07:00 IST (01:30 UTC)
    'sanity-check-weekly': {
        'task':     'sanity.run_checks',
        'schedule': crontab(hour=1, minute=30, day_of_week=1),
        'kwargs':   {'stale_draft_days': 90},
    },
}
