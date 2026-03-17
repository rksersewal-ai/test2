# =============================================================================
# FILE: apps/ocr/tasks.py
# Tasks:
#   compute_attachment_checksum       — FIX #8  (introduced in previous commit)
#   recompute_missing_checksums_task  — FIX #4b (new): Celery Beat wrapper that
#       calls the management-command logic as a Celery task so it can be
#       scheduled via django-celery-beat every 15 minutes.
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
    FIX #4b: Celery Beat wrapper around the recompute_missing_checksums
    management command logic. Finds FileAttachment rows with blank
    checksum_sha256 and computes them synchronously (no sub-tasks) so that
    a Celery downtime never permanently loses checksums.

    Scheduled every 15 minutes via OCRConfig.ready().
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
