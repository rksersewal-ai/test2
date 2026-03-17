# =============================================================================
# FILE: apps/edms/tasks.py
# New file introduced by FIX #8:
#   compute_attachment_checksum — async Celery task that calculates the
#   SHA-256 checksum of a saved FileAttachment and stores it in the DB.
#   Called via transaction.on_commit() in FileAttachmentSerializer.create()
#   to avoid blocking the upload request thread.
# =============================================================================
import hashlib
import logging
import os

from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def compute_attachment_checksum(self, attachment_pk: int):
    """
    Compute SHA-256 of the physical file and save it to
    FileAttachment.checksum_sha256.
    Retries up to 3 times if the file is temporarily unavailable.
    """
    from apps.edms.models import FileAttachment
    try:
        attachment = FileAttachment.objects.get(pk=attachment_pk)
    except FileAttachment.DoesNotExist:
        logger.warning('compute_attachment_checksum: attachment %s not found', attachment_pk)
        return

    try:
        physical_path = attachment.file_path.path
    except (ValueError, AttributeError) as exc:
        logger.error('compute_attachment_checksum: invalid path for attachment %s: %s', attachment_pk, exc)
        return

    if not os.path.exists(physical_path):
        logger.warning('compute_attachment_checksum: file not on disk for attachment %s', attachment_pk)
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
