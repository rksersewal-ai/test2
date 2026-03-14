# =============================================================================
# FILE: config/celery.py
# =============================================================================
import os
from celery          import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('edms_ldo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# =============================================================================
# Celery Beat Schedule
# =============================================================================
app.conf.beat_schedule = {
    # SDR: auto-escalate overdue requests daily at 08:00 IST
    'sdr-escalate-overdue-daily': {
        'task':     'sdr.escalate_overdue_sdrs',
        'schedule': crontab(hour=2, minute=30),  # 08:00 IST = 02:30 UTC
    },
    # SDR: send daily summary to officers at 09:00 IST
    'sdr-daily-summary': {
        'task':     'sdr.send_daily_summary',
        'schedule': crontab(hour=3, minute=30),  # 09:00 IST = 03:30 UTC
    },
    # OCR watch-folder processing every 5 minutes
    'ocr-watch-folder': {
        'task':     'ocr.process_watch_folder',
        'schedule': crontab(minute='*/5'),
    },
    # Audit log archival: daily at midnight IST (18:30 UTC)
    'audit-log-archival': {
        'task':     'audit.archive_old_logs',
        'schedule': crontab(hour=18, minute=30),
    },
    # Work Ledger: monthly report auto-generation on 1st of each month at 06:00 IST
    'work-ledger-monthly-report-gen': {
        'task':     'work_ledger.generate_all_monthly_reports',
        'schedule': crontab(hour=0, minute=30, day_of_month='1'),  # 06:00 IST = 00:30 UTC
    },
}
