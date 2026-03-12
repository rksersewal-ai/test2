"""Celery worker entry point for OCR background tasks.
For Windows: use eventlet or solo pool.
Run: celery -A deployment.celery_worker worker -P solo -l info
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('edms_tasks')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_ocr_file(self, queue_id: int):
    """Celery task: process a single OCR queue item."""
    try:
        from apps.ocr.services import OCRService
        return OCRService.process_file(queue_id)
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task
def process_pending_ocr_queue():
    """Celery periodic task: pick up all PENDING items and dispatch."""
    from apps.ocr.models import OCRQueue
    pending = OCRQueue.objects.filter(
        status__in=[OCRQueue.Status.PENDING, OCRQueue.Status.RETRY]
    ).order_by('priority', 'queued_at')[:20]
    for item in pending:
        process_ocr_file.delay(item.id)
    return f'Dispatched {pending.count()} OCR jobs'
