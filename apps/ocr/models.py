"""OCR queue and result models.

Status flow:
  PENDING → PROCESSING → COMPLETED
                       → FAILED → RETRY → PROCESSING (repeat up to max_attempts)
                       → MANUAL_REVIEW (after max retries)
"""
from django.db import models


class OCRQueue(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        RETRY = 'RETRY', 'Retry'
        MANUAL_REVIEW = 'MANUAL_REVIEW', 'Manual Review'

    file_attachment = models.OneToOneField(
        'edms.FileAttachment', on_delete=models.CASCADE,
        related_name='ocr_queue_item',
    )
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.PENDING, db_index=True,
    )
    priority = models.PositiveSmallIntegerField(default=5)  # 1=highest, 10=lowest
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=3)
    ocr_engine = models.CharField(max_length=40, default='tesseract-5')

    queued_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)

    failure_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'ocr_queue'
        ordering = ['priority', 'queued_at']
        indexes = [
            models.Index(fields=['status', 'priority', 'queued_at']),
        ]

    @property
    def file_name(self):
        return self.file_attachment.file_name

    def __str__(self):
        return f'OCR[{self.status}] {self.file_name}'


class OCRResult(models.Model):
    queue_item = models.OneToOneField(
        OCRQueue, on_delete=models.CASCADE,
        related_name='result',
    )
    full_text = models.TextField(blank=True)
    confidence = models.FloatField(null=True, blank=True)  # 0.0–100.0
    page_count = models.PositiveSmallIntegerField(default=1)
    language_detected = models.CharField(max_length=10, blank=True)
    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ocr_result'

    def __str__(self):
        return f'OCRResult for {self.queue_item.file_name}'


class OCRExtractedEntity(models.Model):
    """Engineering entities parsed from OCR text."""

    class EntityType(models.TextChoices):
        DOCUMENT_NUMBER = 'DOC_NUM', 'Document Number'
        SPECIFICATION = 'SPEC', 'Specification'
        STANDARD = 'STD', 'Standard'
        DRAWING_NUMBER = 'DWG', 'Drawing Number'
        PART_NUMBER = 'PART', 'Part Number'
        DATE = 'DATE', 'Date'
        OTHER = 'OTHER', 'Other'

    result = models.ForeignKey(
        OCRResult, on_delete=models.CASCADE, related_name='entities',
    )
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    value = models.CharField(max_length=500)
    confidence = models.FloatField(null=True, blank=True)
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ocr_extracted_entity'
        indexes = [
            models.Index(fields=['entity_type', 'value']),
        ]

    def __str__(self):
        return f'{self.entity_type}: {self.value}'
