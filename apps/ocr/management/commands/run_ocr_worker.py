"""Management command: python manage.py run_ocr_worker [--loop]

Usage:
  # Process all pending items once, then exit
  python manage.py run_ocr_worker

  # Keep running in a loop (for Windows Task Scheduler / systemd use)
  python manage.py run_ocr_worker --loop --interval 30
"""
import time
import logging
from django.core.management.base import BaseCommand
from apps.ocr.pipeline.worker import run_ocr_worker

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process pending OCR queue items using local Tesseract engine.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loop', action='store_true',
            help='Run continuously (suitable for Windows Task Scheduler keep-alive).'
        )
        parser.add_argument(
            '--interval', type=int, default=30,
            help='Seconds between worker runs in loop mode (default: 30).'
        )

    def handle(self, *args, **options):
        if options['loop']:
            self.stdout.write('OCR worker running in loop mode. Ctrl+C to stop.')
            while True:
                try:
                    run_ocr_worker()
                except KeyboardInterrupt:
                    self.stdout.write('OCR worker stopped.')
                    break
                except Exception as exc:  # noqa: BLE001
                    logger.exception('Worker loop error: %s', exc)
                time.sleep(options['interval'])
        else:
            # Process until queue is empty
            processed = 0
            while True:
                from apps.ocr.models import OCRQueue
                pending = OCRQueue.objects.filter(
                    status__in=[OCRQueue.Status.PENDING, OCRQueue.Status.RETRY]
                ).count()
                if not pending:
                    break
                run_ocr_worker()
                processed += 1
            self.stdout.write(self.style.SUCCESS(f'OCR worker done. Processed {processed} item(s).'))
