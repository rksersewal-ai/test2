# =============================================================================
# FILE: apps/ocr/tasks.py
#
# Tasks:
#   compute_attachment_checksum       — FIX #8 (async SHA-256 after upload)
#   recompute_missing_checksums_task  — FIX #4b (Celery Beat every 15 min)
#   run_ocr_task                      — NEW: wraps OCRService.process_file with
#       max_retries=1 (one Celery retry = total 2 attempts) then marks
#       NOT_OCR_COMPATIBLE on final failure. Idempotent on re-delivery
#       because OCRService.process_file guards against NOT_OCR_COMPATIBLE.
#
# Celery reliability (from settings):
#   CELERY_TASK_ACKS_LATE=True             — message acked after task finishes
#   CELERY_TASK_REJECT_ON_WORKER_LOST=True — re-queued on SIGKILL/OOM
# =============================================================================
import hashlib
import logging
import os
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def compute_attachment_checksum(self, attachment_pk: int):
    """
    FIX #8: Compute SHA-256 of the physical file and save it to
    FileAttachment.checksum_sha256.
    Retries up to 3 times if the file is temporarily unavailable.
    """
    from apps.edms.models import FileAttachment
    try:
        attachment = FileAttachment.objects.get(pk=attachment_pk)
    except FileAttachment.DoesNotExist:
        logger.warning('compute_attachment_checksum: attachment %s not found.', attachment_pk)
        return

    try:
        physical_path = attachment.file_path.path
    except (ValueError, AttributeError) as exc:
        logger.error(
            'compute_attachment_checksum: invalid path for attachment %s: %s',
            attachment_pk, exc,
        )
        return

    if not os.path.exists(physical_path):
        logger.warning(
            'compute_attachment_checksum: file not on disk for attachment %s.',
            attachment_pk,
        )
        return

    sha256 = hashlib.sha256()
    try:
        with open(physical_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                sha256.update(chunk)
    except OSError as exc:
        raise self.retry(exc=exc)

    checksum = sha256.hexdigest()
    FileAttachment.objects.filter(pk=attachment_pk).update(checksum_sha256=checksum)
    logger.info('Checksum computed for attachment %s: %s', attachment_pk, checksum)


@shared_task
def recompute_missing_checksums_task(
    older_than_minutes: int = 5,
    batch_size: int = 50,
):
    """
    FIX #4b: Celery Beat wrapper. Finds FileAttachment rows with blank
    checksum_sha256 and computes them so Celery downtime never permanently
    loses checksums. Scheduled every 15 minutes via OCRConfig.ready().
    """
    from apps.edms.models import FileAttachment

    cutoff_time = timezone.now() - timedelta(minutes=older_than_minutes)
    candidates  = (
        FileAttachment.objects
        .filter(checksum_sha256='', uploaded_at__lt=cutoff_time)
        .order_by('uploaded_at')
        [:batch_size]
    )

    updated = 0
    errors  = 0

    for attachment in candidates:
        try:
            physical_path = attachment.file_path.path
        except (ValueError, AttributeError):
            errors += 1
            continue

        if not os.path.exists(physical_path):
            errors += 1
            continue

        sha256 = hashlib.sha256()
        try:
            with open(physical_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    sha256.update(chunk)
        except OSError as exc:
            logger.error('recompute_missing_checksums_task OSError: %s', exc)
            errors += 1
            continue

        FileAttachment.objects.filter(pk=attachment.pk).update(
            checksum_sha256=sha256.hexdigest()
        )
        updated += 1

    logger.info(
        'recompute_missing_checksums_task: updated=%s errors=%s',
        updated, errors,
    )
    return {'updated': updated, 'errors': errors}


@shared_task(
    bind=True,
    max_retries=1,            # Celery level: 1 retry = total 2 attempts
    default_retry_delay=30,   # wait 30 seconds before retry (transient I/O errors)
    acks_late=True,           # override global setting explicitly for clarity
)
def run_ocr_task(self, queue_id: int):
    """
    Celery task that wraps OCRService.process_file.

    Retry policy (aligned with OCRQueue.max_attempts=2):
      Attempt 1 (Celery try 0):
        - Success              → COMPLETED, done
        - Permanent error      → NOT_OCR_COMPATIBLE immediately (no retry)
        - Transient error      → OCRQueue status=RETRY, Celery retries after 30s

      Attempt 2 (Celery try 1 = self.request.retries == 1):
        - Success              → COMPLETED
        - Any error            → NOT_OCR_COMPATIBLE (max_attempts exhausted)

    The OCRService.process_file method tracks attempts via OCRQueue.attempts
    and decides RETRY vs NOT_OCR_COMPATIBLE. The Celery retry here ensures the
    worker actually picks the job up again after 30s without manual intervention.

    Idempotency: OCRService.process_file checks for NOT_OCR_COMPATIBLE before
    touching the DB, so accidental re-delivery is safe.
    """
    from apps.ocr.services import OCRService, _mark_not_ocr_compatible
    from apps.ocr.models import OCRQueue

    try:
        result = OCRService.process_file(queue_id)
        return {'status': 'completed', 'queue_id': queue_id}
    except Exception as exc:
        error_str = str(exc)
        logger.error(
            'run_ocr_task queue=%s attempt=%s/%s failed: %s',
            queue_id, self.request.retries + 1, self.max_retries + 1, error_str,
        )

        if self.request.retries < self.max_retries:
            # Service already set status=RETRY — let Celery retry after delay
            raise self.retry(exc=exc)
        else:
            # Final attempt exhausted — service will have set NOT_OCR_COMPATIBLE
            # but guard here too in case process_file raised before reaching that code
            try:
                item = OCRQueue.objects.get(pk=queue_id)
                if item.status not in (
                    OCRQueue.Status.COMPLETED,
                    OCRQueue.Status.NOT_OCR_COMPATIBLE,
                ):
                    _mark_not_ocr_compatible(item, reason=f'Celery max_retries exhausted: {error_str}')
            except OCRQueue.DoesNotExist:
                pass
            logger.warning(
                'run_ocr_task queue=%s permanently marked NOT_OCR_COMPATIBLE after %s attempts.',
                queue_id, self.max_retries + 1,
            )
            return {'status': 'not_ocr_compatible', 'queue_id': queue_id}
