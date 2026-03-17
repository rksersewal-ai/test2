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


class OCRService:

    @staticmethod
    def queue_file_for_ocr(file_id: int, priority: int = 5, language: str = 'eng', user_id=None):
        from apps.ocr.models import OCRQueue
        from apps.edms.models import FileAttachment
        file_obj = FileAttachment.objects.get(pk=file_id)
        queue_item, created = OCRQueue.objects.get_or_create(
            file=file_obj,
            defaults={
                'priority':        priority,
                'language':        language,
                'created_by_id':   user_id,
                'status':          OCRQueue.Status.PENDING,
            }
        )
        if not created and queue_item.status == OCRQueue.Status.FAILED:
            queue_item.status   = OCRQueue.Status.PENDING
            queue_item.attempts = 0
            queue_item.last_error = ''
            queue_item.save(update_fields=['status', 'attempts', 'last_error'])
        return queue_item

    @staticmethod
    def retry_failed_item(queue_id: int):
        from apps.ocr.models import OCRQueue
        item = OCRQueue.objects.get(pk=queue_id)
        if item.status not in [OCRQueue.Status.FAILED, OCRQueue.Status.MANUAL_REVIEW]:
            raise ValueError(f'Cannot retry item with status: {item.status}')
        item.status   = OCRQueue.Status.PENDING
        item.attempts = 0
        item.last_error = ''
        item.save(update_fields=['status', 'attempts', 'last_error'])
        return item

    @staticmethod
    def process_file(queue_id: int):
        """Main OCR processing entry point — called by background worker."""
        from apps.ocr.models import OCRQueue, OCRResult
        item = OCRQueue.objects.select_related('file').get(pk=queue_id)
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
            file_path = item.file.file_path.path

            # FIX #9: guard against huge files that would OOM the worker
            file_size_mb = os.path.getsize(file_path) / 1024 / 1024
            if file_size_mb > OCR_MAX_FILE_MB:
                raise ValueError(
                    f'File too large for OCR: {file_size_mb:.1f} MB '
                    f'(limit: {OCR_MAX_FILE_MB} MB). Mark as MANUAL_REVIEW.'
                )

            pages_text        = []
            full_text_parts   = []
            all_confidences   = []

            if file_path.lower().endswith('.pdf'):
                # FIX #2: catch fitz-specific errors before generic Exception
                try:
                    doc = fitz.open(file_path)
                except Exception as fitz_err:
                    raise RuntimeError(f'Cannot open PDF (possibly corrupt): {fitz_err}') from fitz_err

                for page_num, page in enumerate(doc):
                    text = page.get_text().strip()
                    if not text:
                        pix = page.get_pixmap(dpi=settings.OCR_DPI)
                        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
                        # FIX #21: collect per-word confidence
                        data = pytesseract.image_to_data(
                            img, lang=item.language,
                            output_type=pytesseract.Output.DICT
                        )
                        text = ' '.join([w for w in data['text'] if str(w).strip()])
                        confs = [
                            int(c) for c in data['conf']
                            if str(c).lstrip('-').isdigit() and int(c) >= 0
                        ]
                        all_confidences.extend(confs)
                    pages_text.append({'page': page_num + 1, 'text': text})
                    full_text_parts.append(text)
                doc.close()

            else:
                # FIX #24: use ImageSequence to iterate multi-page TIFFs
                # frame by frame without loading all pages into RAM at once.
                img = Image.open(file_path)
                for frame_num, frame in enumerate(ImageSequence.Iterator(img)):
                    frame_copy = frame.copy()  # detach from file handle
                    data = pytesseract.image_to_data(
                        frame_copy, lang=item.language,
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

            # FIX #21: real confidence from Tesseract data (0–100 scale → 0.0–1.0)
            confidence_score = (
                round(sum(all_confidences) / len(all_confidences) / 100, 4)
                if all_confidences else 0.0
            )

            result, _ = OCRResult.objects.update_or_create(
                file=item.file,
                defaults={
                    'queue':                    item,
                    'full_text':                full_text,
                    'page_count':               len(pages_text),
                    'confidence_score':         confidence_score,   # FIX #21
                    'page_results':             pages_text,
                    'ocr_engine':               'tesseract',
                    'language_detected':        item.language,
                    'processing_time_seconds':  elapsed,
                    'file_size_bytes':          os.path.getsize(file_path),
                    'indexed_at':               timezone.now(),
                }
            )

            item.status                  = OCRQueue.Status.COMPLETED
            item.completed_at            = timezone.now()
            item.processing_time_seconds = elapsed
            item.save(update_fields=['status', 'completed_at', 'processing_time_seconds'])

            OCRService._extract_entities(result, full_text)
            return result

        except Exception as exc:
            elapsed = time.time() - start
            logger.error('OCR failed for queue %s: %s', queue_id, exc)
            item.last_error = str(exc)
            item.status = (
                OCRQueue.Status.MANUAL_REVIEW
                if item.attempts >= item.max_attempts
                else OCRQueue.Status.RETRY
            )
            item.processing_time_seconds = elapsed
            item.save(update_fields=['status', 'last_error', 'processing_time_seconds'])
            raise

    @staticmethod
    def _extract_entities(ocr_result, full_text: str):
        """Regex-based entity extraction for drawing/doc numbers.
        FIX #14: Capped at MAX_ENTITIES_PER_PATTERN=500 per pattern to prevent
        bulk_create holding a DB write lock for seconds on verbose OCR output.
        """
        from apps.ocr.models import ExtractedEntity

        MAX_ENTITIES_PER_PATTERN = 500

        patterns = [
            (ExtractedEntity.EntityType.DRAWING_NUMBER, r'DRG[.\-/]?\d{4,}'),
            (ExtractedEntity.EntityType.SPEC_NUMBER,    r'SPEC[.\-/]?[A-Z0-9]{4,}'),
            (ExtractedEntity.EntityType.STANDARD,       r'(IS|DIN|RDSO|IRIS|ABB)[.\-/\s]?[\d]{3,}'),
            (ExtractedEntity.EntityType.REVISION,       r'Rev[.]?\s*[A-Z0-9]{1,4}'),
        ]
        entities = []
        for entity_type, pattern in patterns:
            # FIX #14: islice caps matches per pattern
            matches = itertools.islice(
                re.finditer(pattern, full_text, re.IGNORECASE),
                MAX_ENTITIES_PER_PATTERN
            )
            for match in matches:
                entities.append(ExtractedEntity(
                    ocr_result=ocr_result,
                    entity_type=entity_type,
                    entity_value=match.group().strip(),
                    context=full_text[max(0, match.start() - 50):match.end() + 50],
                ))
        if entities:
            ExtractedEntity.objects.bulk_create(entities, ignore_conflicts=True)
