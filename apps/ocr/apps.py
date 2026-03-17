# =============================================================================
# FILE: apps/ocr/apps.py
# FIX #3b : Wire check_tesseract_available() into AppConfig.ready()
# FIX #4b : Register the recompute_missing_checksums Celery Beat periodic
#           task in ready() so it runs every 15 minutes automatically.
#           No manual django-celery-beat admin config needed.
# =============================================================================
import sys
from django.apps import AppConfig


class OCRConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.ocr'
    verbose_name       = 'OCR Pipeline'

    def ready(self):
        # Skip side-effectful setup during DB/static management commands
        _skip_cmds = {'migrate', 'makemigrations', 'collectstatic', 'test', 'shell'}
        if any(cmd in sys.argv for cmd in _skip_cmds):
            return

        # FIX #3b: Tesseract binary health check at startup
        try:
            from apps.ocr.services import check_tesseract_available
            check_tesseract_available()
        except Exception:
            import logging
            logging.getLogger(__name__).warning(
                'Tesseract health check raised an unexpected error at startup. '
                'OCR processing may be unavailable.'
            )

        # FIX #4b: Register periodic beat task for checksum fallback poller
        # Uses get_or_create so it is idempotent across restarts.
        self._register_checksum_beat_task()

    @staticmethod
    def _register_checksum_beat_task():
        """Ensure the recompute_missing_checksums beat task exists in DB.
        Runs every 15 minutes. Safe to call multiple times (idempotent).
        """
        try:
            from django_celery_beat.models import PeriodicTask, IntervalSchedule
            import json

            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=15,
                period=IntervalSchedule.MINUTES,
            )
            PeriodicTask.objects.get_or_create(
                name='recompute-missing-checksums',
                defaults={
                    'task':     'apps.ocr.tasks.recompute_missing_checksums_task',
                    'interval': schedule,
                    'args':     json.dumps([]),
                    'kwargs':   json.dumps({}),
                    'enabled':  True,
                },
            )
        except Exception:
            # DB may not yet have celery_beat tables (first deploy before migrate)
            import logging
            logging.getLogger(__name__).debug(
                'Could not register checksum beat task — '
                'run migrate first if this is a fresh deployment.'
            )
