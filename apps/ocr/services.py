"""OCR service layer - queue management and Tesseract pipeline."""
import os
import time
import hashlib
import logging
from datetime import datetime
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class OCRService:

    @staticmethod
    def queue_file_for_ocr(file_id: int, priority: int = 5, language: str = 'eng', user_id=None):
        from apps.ocr.models import OCRQueue
        from apps.edms.models import FileAttachment
        file_obj = FileAttachment.objects.get(pk=file_id)
        queue_item, created = OCRQueue.objects.get_or_create(
            file=file_obj,
            defaults={
                'priority': priority,
                'language': language,
                'created_by_id': user_id,
                'status': OCRQueue.Status.PENDING,
            }
        )
        if not created and queue_item.status == OCRQueue.Status.FAILED:
            queue_item.status = OCRQueue.Status.PENDING
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
        item.status = OCRQueue.Status.PENDING
        item.attempts = 0
        item.last_error = ''
        item.save(update_fields=['status', 'attempts', 'last_error'])
        return item

    @staticmethod
    def process_file(queue_id: int):
        """Main OCR processing entry - called by background worker."""
        from apps.ocr.models import OCRQueue, OCRResult
        item = OCRQueue.objects.select_related('file').get(pk=queue_id)
        item.status = OCRQueue.Status.PROCESSING
        item.started_at = timezone.now()
        item.attempts += 1
        item.save(update_fields=['status', 'started_at', 'attempts'])

        start = time.time()
        try:
            import pytesseract
            from PIL import Image
            import fitz  # PyMuPDF

            pytesseract.pytesseract.tesseract_cmd = settings.OCR_TESSERACT_CMD
            file_path = item.file.file_path.path

            pages_text = []
            full_text_parts = []

            if file_path.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                for page_num, page in enumerate(doc):
                    # Check if text-based PDF
                    text = page.get_text().strip()
                    if not text:
                        pix = page.get_pixmap(dpi=settings.OCR_DPI)
                        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
                        text = pytesseract.image_to_string(img, lang=item.language)
                    pages_text.append({'page': page_num + 1, 'text': text})
                    full_text_parts.append(text)
                doc.close()
            else:
                img = Image.open(file_path)
                data = pytesseract.image_to_data(img, lang=item.language, output_type=pytesseract.Output.DICT)
                text = ' '.join([w for w in data['text'] if w.strip()])
                pages_text.append({'page': 1, 'text': text})
                full_text_parts.append(text)

            full_text = '\n'.join(full_text_parts)
            elapsed = time.time() - start

            result, _ = OCRResult.objects.update_or_create(
                file=item.file,
                defaults={
                    'queue': item,
                    'full_text': full_text,
                    'page_count': len(pages_text),
                    'confidence_score': 0.85,
                    'page_results': pages_text,
                    'ocr_engine': 'tesseract',
                    'language_detected': item.language,
                    'processing_time_seconds': elapsed,
                    'file_size_bytes': os.path.getsize(file_path),
                    'indexed_at': timezone.now(),
                }
            )

            item.status = OCRQueue.Status.COMPLETED
            item.completed_at = timezone.now()
            item.processing_time_seconds = elapsed
            item.save(update_fields=['status', 'completed_at', 'processing_time_seconds'])

            OCRService._extract_entities(result, full_text)
            return result

        except Exception as exc:
            elapsed = time.time() - start
            logger.error(f'OCR failed for queue {queue_id}: {exc}')
            item.last_error = str(exc)
            if item.attempts >= item.max_attempts:
                item.status = OCRQueue.Status.MANUAL_REVIEW
            else:
                item.status = OCRQueue.Status.RETRY
            item.processing_time_seconds = elapsed
            item.save(update_fields=['status', 'last_error', 'processing_time_seconds'])
            raise

    @staticmethod
    def _extract_entities(ocr_result, full_text: str):
        """Simple regex-based entity extraction for drawing/doc numbers."""
        import re
        from apps.ocr.models import ExtractedEntity
        patterns = [
            (ExtractedEntity.EntityType.DRAWING_NUMBER, r'DRG[.\-/]?\d{4,}'),
            (ExtractedEntity.EntityType.SPEC_NUMBER, r'SPEC[.\-/]?[A-Z0-9]{4,}'),
            (ExtractedEntity.EntityType.STANDARD, r'(IS|DIN|RDSO|IRIS|ABB)[.\-/\s]?[\d]{3,}'),
            (ExtractedEntity.EntityType.REVISION, r'Rev[.]?\s*[A-Z0-9]{1,4}'),
        ]
        entities = []
        for entity_type, pattern in patterns:
            for match in re.finditer(pattern, full_text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    ocr_result=ocr_result,
                    entity_type=entity_type,
                    entity_value=match.group().strip(),
                    context=full_text[max(0, match.start()-50):match.end()+50],
                ))
        if entities:
            ExtractedEntity.objects.bulk_create(entities, ignore_conflicts=True)
