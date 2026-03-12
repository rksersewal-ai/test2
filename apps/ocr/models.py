"""OCR Pipeline models - queue, result, extracted entities."""
from django.db import models
from django.conf import settings


class OCRQueue(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        RETRY = 'RETRY', 'Retry'
        MANUAL_REVIEW = 'MANUAL_REVIEW', 'Manual Review'

    file = models.OneToOneField('edms.FileAttachment', on_delete=models.CASCADE, related_name='ocr_queue')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    priority = models.IntegerField(default=5, help_text='1=highest, 10=lowest')
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    ocr_engine = models.CharField(max_length=50, default='tesseract')
    language = models.CharField(max_length=10, default='eng')
    preprocessing_options = models.JSONField(default=dict, blank=True)
    worker_id = models.CharField(max_length=100, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='ocr_queue_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ocr_queue'
        ordering = ['priority', 'queued_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['status', 'queued_at']),
        ]

    def __str__(self):
        return f"OCR Queue #{self.id} [{self.status}] - {self.file.file_name}"


class OCRResult(models.Model):
    file = models.OneToOneField('edms.FileAttachment', on_delete=models.CASCADE, related_name='ocr_result')
    queue = models.OneToOneField(OCRQueue, null=True, on_delete=models.SET_NULL, related_name='result')
    full_text = models.TextField(blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    page_results = models.JSONField(default=list, help_text='Per-page OCR text and confidence')
    ocr_engine = models.CharField(max_length=50, default='tesseract')
    ocr_version = models.CharField(max_length=30, blank=True)
    language_detected = models.CharField(max_length=10, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    indexed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ocr_result'

    def __str__(self):
        return f"OCR Result for {self.file.file_name} (conf: {self.confidence_score})"


class ExtractedEntity(models.Model):
    class EntityType(models.TextChoices):
        DOCUMENT_NUMBER = 'DOC_NUM', 'Document Number'
        SPEC_NUMBER = 'SPEC_NUM', 'Specification Number'
        STANDARD = 'STANDARD', 'Standard Reference'
        DRAWING_NUMBER = 'DRG_NUM', 'Drawing Number'
        DATE = 'DATE', 'Date'
        REVISION = 'REVISION', 'Revision'
        KEYWORD = 'KEYWORD', 'Keyword'
        OTHER = 'OTHER', 'Other'

    ocr_result = models.ForeignKey(OCRResult, on_delete=models.CASCADE, related_name='entities')
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    entity_value = models.CharField(max_length=300, db_index=True)
    confidence = models.FloatField(null=True, blank=True)
    context = models.TextField(blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    bounding_box = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ocr_extracted_entity'
        indexes = [
            models.Index(fields=['entity_type', 'entity_value']),
        ]
