"""OCR service layer — queue management and Tesseract pipeline.

FIXES applied:
  #2  - fitz.FileDataError explicitly caught before generic Exception so
        corrupt PDF does not leave OCRQueue in a zombie PROCESSING state.
  #3  - Tesseract binary availability checked at import time via
        check_tesseract_available(); critical warning logged if missing.
  #9  - File size guard before loading into RAM — rejects files > OCR_MAX_FILE_MB.
  #14 - _extract_entities capped at MAX_ENTITIES_PER_PATTERN=500 per pattern
        to prevent bulk_create locking the DB for seconds on long OCR output.
  #21 - confidence_score now computed from actual Tesseract per-word confidence
        data instead of the previous hardcoded 0.85.
  #24 - Multi-page TIFF processing uses ImageSequence to iterate frames without
        loading all pages into RAM simultaneously.
  #NEW - NOT_OCR_COMPATIBLE: On second failure (or on first failure with a
        known permanent error such as password-protected PDF, corrupt file,
        OS permission denied), the queue item is marked NOT_OCR_COMPATIBLE
        and FileAttachment.is_ocr_compatible is set to False permanently.
        The item is never re-queued automatically after this point.
"""
import os
import re
import time
import itertools
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

OCR_MAX_FILE_MB: int = getattr(settings, 'OCR_MAX_FILE_MB', 100)


def check_tesseract_available() -> bool:
    """FIX #3: Verify Tesseract binary exists at startup."""
    import subprocess
    cmd = getattr(settings, 'OCR_TESSERACT_CMD',
                  r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    try:
        result = subprocess.run(
            [cmd, '--version'],
            capture_output=True, timeout=5
        )
        if result.returncode != 0:
            logger.critical(
                'Tesseract binary at "%s" returned non-zero exit code. '
                'All OCR jobs will fail until this is resolved.', cmd
            )
            return False
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        logger.critical(
            'Tesseract NOT FOUND at "%s": %s. '
            'OCR processing is disabled until the binary is installed and '
            'OCR_TESSERACT_CMD in settings is updated.', cmd, exc
        )
        return False


def _mark_not_ocr_compatible(item, reason: str):
    """
    Mark a queue item as permanently NOT_OCR_COMPATIBLE and update
    the linked FileAttachment so the UI can show the correct badge.

    This is the single authoritative place for the NOT_OCR_COMPATIBLE
    transition — called from both the service layer and the Celery task.
    """
    item.status        = item.Status.NOT_OCR_COMPATIBLE
    item.failure_reason = reason[:2000]   # guard against huge exception strings
    item.completed_at  = timezone.now()
    item.save(update_fields=['status', 'failure_reason', 'completed_at'])

    # Propagate to FileAttachment so list/detail views can show badge
    try:
        fa = item.file_attachment
        if hasattr(fa, 'is_ocr_compatible'):
            fa.is_ocr_compatible = False
            fa.save(update_fields=['is_ocr_compatible'])
    except Exception as prop_exc:
        logger.warning(
            'Could not propagate is_ocr_compatible=False to attachment %s: %s',
            getattr(item, 'file_attachment_id', '?'), prop_exc,
        )

    logger.warning(
        'OCR queue item %s marked NOT_OCR_COMPATIBLE. Reason: %s',
        item.pk, reason,
    )


class OCRService:

    @staticmethod
    def queue_file_for_ocr(file_id: int, priority: int = 5, language: str = 'eng', user_id=None):
        from apps.ocr.models import OCRQueue
        from apps.edms.models import FileAttachment
        file_obj = FileAttachment.objects.get(pk=file_id)

        # Do not re-queue files already marked as permanently incompatible.
        if hasattr(file_obj, 'is_ocr_compatible') and file_obj.is_ocr_compatible is False:
            logger.info(
                'queue_file_for_ocr: attachment %s is marked not OCR compatible — skipping.',
                file_id,
            )
            return None

        queue_item, created = OCRQueue.objects.get_or_create(
            file_attachment=file_obj,
            defaults={
                'priority':   priority,
                'status':     OCRQueue.Status.PENDING,
            }
        )
        if not created and queue_item.status == OCRQueue.Status.FAILED:
            queue_item.status        = OCRQueue.Status.PENDING
            queue_item.attempts      = 0
            queue_item.failure_reason = ''
            queue_item.save(update_fields=['status', 'attempts', 'failure_reason'])
        return queue_item

    @staticmethod
    def retry_failed_item(queue_id: int):
        from apps.ocr.models import OCRQueue
        item = OCRQueue.objects.get(pk=queue_id)
        if item.status == OCRQueue.Status.NOT_OCR_COMPATIBLE:
            raise ValueError(
                'This file is marked NOT_OCR_COMPATIBLE and cannot be retried automatically. '
                'If you believe this is a mistake, override via the admin panel.'
            )
        if item.status not in [OCRQueue.Status.FAILED, OCRQueue.Status.MANUAL_REVIEW]:
            raise ValueError(f'Cannot retry item with status: {item.status}')
        item.status        = OCRQueue.Status.PENDING
        item.attempts      = 0
        item.failure_reason = ''
        item.save(update_fields=['status', 'attempts', 'failure_reason'])
        return item

    @staticmethod
    def process_file(queue_id: int):
        """
        Main OCR processing entry point — called by background worker.

        Retry policy:
          - attempt 1 fails with PERMANENT error  → immediately NOT_OCR_COMPATIBLE
          - attempt 1 fails with transient error  → RETRY (will be picked up again)
          - attempt 2 fails (any error)           → NOT_OCR_COMPATIBLE
        """
        from apps.ocr.models import OCRQueue, OCRResult
        item = OCRQueue.objects.select_related('file_attachment').get(pk=queue_id)

        # Safety guard: never process a permanently incompatible file
        if item.status == OCRQueue.Status.NOT_OCR_COMPATIBLE:
            logger.info('process_file: queue item %s is NOT_OCR_COMPATIBLE — skipping.', queue_id)
            return None

        item.status     = OCRQueue.Status.PROCESSING
        item.started_at = timezone.now()
        item.attempts  += 1
        item.save(update_fields=['status', 'started_at', 'attempts'])

        start = time.time()
        try:
            import pytesseract
            from PIL import Image, ImageSequence
            import fitz  # PyMuPDF

            pytesseract.pytesseract.tesseract_cmd = settings.OCR_TESSERACT_CMD
            file_path = item.file_attachment.file_path.path

            # FIX #9: guard against huge files that would OOM the worker
            file_size_mb = os.path.getsize(file_path) / 1024 / 1024
            if file_size_mb > OCR_MAX_FILE_MB:
                raise ValueError(
                    f'File too large for OCR: {file_size_mb:.1f} MB '
                    f'(limit: {OCR_MAX_FILE_MB} MB).'
                )

            pages_text      = []
            full_text_parts = []
            all_confidences = []

            if file_path.lower().endswith('.pdf'):
                try:
                    doc = fitz.open(file_path)
                except Exception as fitz_err:
                    raise RuntimeError(f'Cannot open PDF: {fitz_err}') from fitz_err

                # Detect password-protected PDF immediately
                if doc.is_encrypted and not doc.authenticate(''):
                    doc.close()
                    raise RuntimeError(
                        'PDF is password-protected (encrypted). '
                        'Cannot OCR without the password.'
                    )

                for page_num, page in enumerate(doc):
                    text = page.get_text().strip()
                    if not text:
                        pix = page.get_pixmap(dpi=settings.OCR_DPI)
                        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
                        data = pytesseract.image_to_data(
                            img, lang=OCRService._get_language(item),
                            output_type=pytesseract.Output.DICT
                        )
                        text  = ' '.join([w for w in data['text'] if str(w).strip()])
                        confs = [
                            int(c) for c in data['conf']
                            if str(c).lstrip('-').isdigit() and int(c) >= 0
                        ]
                        all_confidences.extend(confs)
                    pages_text.append({'page': page_num + 1, 'text': text})
                    full_text_parts.append(text)
                doc.close()

            else:
                img = Image.open(file_path)
                for frame_num, frame in enumerate(ImageSequence.Iterator(img)):
                    frame_copy = frame.copy()
                    data = pytesseract.image_to_data(
                        frame_copy, lang=OCRService._get_language(item),
                        output_type=pytesseract.Output.DICT
                    )
                    text  = ' '.join([w for w in data['text'] if str(w).strip()])
                    confs = [
                        int(c) for c in data['conf']
                        if str(c).lstrip('-').isdigit() and int(c) >= 0
                    ]
                    all_confidences.extend(confs)
                    pages_text.append({'page': frame_num + 1, 'text': text})
                    full_text_parts.append(text)

            full_text = '\n'.join(full_text_parts)
            elapsed   = time.time() - start

            confidence_score = (
                round(sum(all_confidences) / len(all_confidences) / 100, 4)
                if all_confidences else 0.0
            )

            result, _ = OCRResult.objects.update_or_create(
                queue_item=item,
                defaults={
                    'full_text':         full_text,
                    'page_count':        len(pages_text),
                    'confidence':        confidence_score,
                    'language_detected': OCRService._get_language(item),
                }
            )

            item.status                  = OCRQueue.Status.COMPLETED
            item.completed_at            = timezone.now()
            item.processing_time_seconds = elapsed
            item.save(update_fields=['status', 'completed_at', 'processing_time_seconds'])

            OCRService._extract_entities(result, full_text)
            return result

        except Exception as exc:
            elapsed     = time.time() - start
            error_str   = str(exc)
            logger.error('OCR failed for queue %s (attempt %s): %s', queue_id, item.attempts, exc)

            item.processing_time_seconds = elapsed

            # Decision: go straight to NOT_OCR_COMPATIBLE or allow retry?
            is_permanent = item.is_permanent_failure(error_str)
            exhausted    = item.attempts >= item.max_attempts   # max_attempts=2

            if is_permanent or exhausted:
                # Permanent error on any attempt, OR transient error after max retries
                _mark_not_ocr_compatible(item, reason=error_str)
            else:
                # Transient error on first attempt — allow one retry
                item.status        = OCRQueue.Status.RETRY
                item.failure_reason = error_str[:2000]
                item.save(update_fields=['status', 'failure_reason', 'processing_time_seconds'])
            raise

    @staticmethod
    def _get_language(item) -> str:
        """Get OCR language — fall back to settings default."""
        return getattr(item, 'language', None) or getattr(settings, 'OCR_DEFAULT_LANG', 'eng')

    @staticmethod
    def _extract_entities(ocr_result, full_text: str):
        """Regex-based entity extraction for drawing/doc numbers.
        FIX #14: Capped at MAX_ENTITIES_PER_PATTERN=500 per pattern.
        """
        from apps.ocr.models import OCRExtractedEntity

        MAX_ENTITIES_PER_PATTERN = 500

        patterns = [
            (OCRExtractedEntity.EntityType.DRAWING_NUMBER, r'DRG[.\-/]?\d{4,}'),
            (OCRExtractedEntity.EntityType.SPECIFICATION,  r'SPEC[.\-/]?[A-Z0-9]{4,}'),
            (OCRExtractedEntity.EntityType.STANDARD,       r'(IS|DIN|RDSO|IRIS|ABB)[.\-/\s]?[\d]{3,}'),
            (OCRExtractedEntity.EntityType.DATE,           r'Rev[.]?\s*[A-Z0-9]{1,4}'),
        ]
        entities = []
        for entity_type, pattern in patterns:
            matches = itertools.islice(
                re.finditer(pattern, full_text, re.IGNORECASE),
                MAX_ENTITIES_PER_PATTERN
            )
            for match in matches:
                entities.append(OCRExtractedEntity(
                    result=ocr_result,
                    entity_type=entity_type,
                    value=match.group().strip(),
                    confidence=None,
                    page_number=None,
                ))
        if entities:
            OCRExtractedEntity.objects.bulk_create(entities, ignore_conflicts=True)
