# =============================================================================
# FILE: celery_app.py
# FIX #6: DJANGO_SETTINGS_MODULE was 'config.settings' which is a package,
#         not a module. Must point to config.settings.development or
#         config.settings.production. Defaults to development; override
#         via DJANGO_SETTINGS_MODULE env var in production.
#
# FIX #13: Corrected all task name strings to match actual @shared_task
#          registered names (module.function_name format).
# =============================================================================
import os
from celery import Celery
from celery.schedules import crontab

# FIX #6: was 'config.settings' (package dir, not importable as module)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('edms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # ---- Sprint 4 -------------------------------------------------------
    # FIX #13: corrected task name paths
    'purge-expired-notifications': {
        'task':     'apps.notifications.tasks.purge_expired',
        'schedule': crontab(hour=20, minute=30),
    },
    'purge-old-read-notifications': {
        'task':     'apps.notifications.tasks.purge_old_read',
        'schedule': crontab(hour=21, minute=30, day_of_week=0),
    },
    'overdue-work-reminders': {
        'task':     'apps.notifications.tasks.overdue_work_reminders',
        'schedule': crontab(hour=2, minute=30),
    },
    'approval-sla-reminders': {
        'task':     'apps.notifications.tasks.approval_sla_reminders',
        'schedule': crontab(hour=3, minute=30),
    },
    # ---- Sprint 5 -------------------------------------------------------
    'ml-retrain-weekly': {
        'task':     'apps.ml_classifier.tasks.retrain_all',
        'schedule': crontab(hour=19, minute=30, day_of_week=0),
        'kwargs':   {'user_id': None},
    },
    # ---- Sprint 6 -------------------------------------------------------
    'sanity-check-weekly': {
        'task':     'apps.sanity.tasks.run_checks',
        'schedule': crontab(hour=1, minute=30, day_of_week=1),
        'kwargs':   {'stale_draft_days': 90},
    },
    # ---- Sprint 7 -------------------------------------------------------
    'purge-expired-sharelinks': {
        'task':     'apps.sharelinks.tasks.purge_expired',
        'schedule': crontab(hour=19, minute=0),
    },
    'purge-old-webhook-deliveries': {
        'task':     'apps.webhooks.tasks_maintenance.purge_old_deliveries',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),
        'kwargs':   {'days': 30},
    },
}
