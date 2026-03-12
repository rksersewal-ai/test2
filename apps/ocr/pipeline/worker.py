"""OCR worker — processes one OCRQueue item at a time.

Called by scheduler (APScheduler/django-apscheduler) or management command.
All processing is local-only; no outbound network calls.

Stages:
  1. Claim PENDING/RETRY item (atomic update to PROCESSING)
  2. Detect file type
  3. If text-PDF → extract with pdfminer; skip Tesseract
  4. If image/scanned-PDF → convert pages → preprocess → Tesseract OCR
  5. Parse extracted entities
  6. Persist OCRResult and OCRExtractedEntity rows
  7. Update FileAttachment.ocr_status
  8. Mark queue item COMPLETED / FAILED
"""
import time
import logging
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


def run_ocr_worker():
    """Entry point: claim and process one queued item."""
    from apps.ocr.models import OCRQueue
    from apps.edms.models import FileAttachment

    # Atomic claim — prevents duplicate processing on multi-process deployments
    with transaction.atomic():
        item = (
            OCRQueue.objects
            .select_for_update(skip_locked=True)
            .filter(status__in=[OCRQueue.Status.PENDING, OCRQueue.Status.RETRY])
            .order_by('priority', 'queued_at')
            .first()
        )
        if item is None:
            return  # Nothing to process
        item.status = OCRQueue.Status.PROCESSING
        item.started_at = timezone.now()
        item.attempts += 1
        item.save(update_fields=['status', 'started_at', 'attempts'])

    t0 = time.perf_counter()
    try:
        _process(item)
        elapsed = time.perf_counter() - t0
        item.status = OCRQueue.Status.COMPLETED
        item.completed_at = timezone.now()
        item.processing_time_seconds = elapsed
        item.save(update_fields=['status', 'completed_at', 'processing_time_seconds'])

        # Sync status back to FileAttachment
        FileAttachment.objects.filter(pk=item.file_attachment_id).update(
            ocr_status=FileAttachment.OCRStatus.COMPLETED
        )
        logger.info('OCR completed: %s in %.2fs', item.file_name, elapsed)

    except Exception as exc:  # noqa: BLE001
        logger.exception('OCR failed for %s: %s', item.file_name, exc)
        item.failure_reason = str(exc)
        if item.attempts >= item.max_attempts:
            item.status = OCRQueue.Status.MANUAL_REVIEW
            FileAttachment.objects.filter(pk=item.file_attachment_id).update(
                ocr_status=FileAttachment.OCRStatus.MANUAL_REVIEW
            )
        else:
            item.status = OCRQueue.Status.FAILED
            FileAttachment.objects.filter(pk=item.file_attachment_id).update(
                ocr_status=FileAttachment.OCRStatus.FAILED
            )
        item.completed_at = timezone.now()
        item.save(update_fields=['status', 'failure_reason', 'completed_at'])


def _process(item):
    """Core extraction — delegates to preprocessor and extractor."""
    from apps.ocr.pipeline.extractor import extract_text_and_confidence
    from apps.ocr.pipeline.entity_parser import parse_entities
    from apps.ocr.models import OCRResult

    fa = item.file_attachment
    file_path = fa.file.path  # Django FileField path

    full_text, confidence, page_count = extract_text_and_confidence(file_path)

    result = OCRResult.objects.create(
        queue_item=item,
        full_text=full_text,
        confidence=confidence,
        page_count=page_count,
    )
    entities = parse_entities(full_text)
    for ent in entities:
        from apps.ocr.models import OCRExtractedEntity
        OCRExtractedEntity.objects.create(
            result=result,
            entity_type=ent['type'],
            value=ent['value'],
            confidence=ent.get('confidence'),
        )
