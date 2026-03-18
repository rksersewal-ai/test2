"""OCR queue and result models.

Status flow:
  PENDING → PROCESSING → COMPLETED
                       → FAILED
                           ├─ attempts < 2  → RETRY → PROCESSING (one retry)
                           └─ attempts >= 2 → NOT_OCR_COMPATIBLE (permanent skip)

NOT_OCR_COMPATIBLE is set when:
  - PDF is password-protected / encrypted
  - File is corrupt and cannot be opened
  - Tesseract raises an unrecoverable error on retry
  - File type is unsupported by the OCR pipeline

Once NOT_OCR_COMPATIBLE, the queue item is never re-queued automatically.
A human admin can manually override via the admin panel if needed.
"""
from django.db import models


class OCRQueue(models.Model):
    class Status(models.TextChoices):
        PENDING              = 'PENDING',              'Pending'
        PROCESSING           = 'PROCESSING',           'Processing'
        COMPLETED            = 'COMPLETED',            'Completed'
        FAILED               = 'FAILED',               'Failed'
        CANCELLED            = 'CANCELLED',            'Cancelled'
        RETRY                = 'RETRY',                'Retry'
        MANUAL_REVIEW        = 'MANUAL_REVIEW',        'Manual Review'
        NOT_OCR_COMPATIBLE   = 'NOT_OCR_COMPATIBLE',   'Not OCR Compatible'

    # Errors that immediately indicate a file cannot be processed by OCR.
    # On first failure with one of these, skip the retry and go straight
    # to NOT_OCR_COMPATIBLE. On any other error, allow one retry first.
    PERMANENT_FAILURE_MARKERS = [
        'password',       # PDF password-protected
        'encrypted',      # PDF encrypted
        'cannot open',    # fitz cannot parse the file at all
        'unsupported',    # file type not supported
        'not a pdf',      # magic-byte mismatch
        'no objects',     # completely empty/corrupt PDF
        'corrupt',        # generic corruption signal
        'permission',     # OS-level read permission denied
    ]

    file_attachment = models.OneToOneField(
        'edms.FileAttachment', on_delete=models.CASCADE,
        related_name='ocr_queue_item',
    )
    status = models.CharField(
        max_length=25, choices=Status.choices,
        default=Status.PENDING, db_index=True,
    )
    priority = models.PositiveSmallIntegerField(default=5)  # 1=highest, 10=lowest
    attempts = models.PositiveSmallIntegerField(default=0)
    # max_attempts is now effectively 2:
    #   attempt 1 → RETRY if error is non-permanent
    #   attempt 2 → NOT_OCR_COMPATIBLE if still failing
    max_attempts = models.PositiveSmallIntegerField(default=2)
    ocr_engine = models.CharField(max_length=40, default='tesseract-5')

    queued_at    = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at   = models.DateTimeField(null=True, blank=True)
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

    def is_permanent_failure(self, error_message: str) -> bool:
        """
        Return True if the error message matches a known permanent failure
        pattern that means the file can never be OCR-processed.
        """
        msg_lower = error_message.lower()
        return any(marker in msg_lower for marker in self.PERMANENT_FAILURE_MARKERS)

    def __str__(self):
        return f'OCR[{self.status}] {self.file_name}'


class OCRResult(models.Model):
    queue_item = models.OneToOneField(
        OCRQueue, on_delete=models.CASCADE,
        related_name='result',
    )
    full_text          = models.TextField(blank=True)
    confidence         = models.FloatField(null=True, blank=True)  # 0.0–100.0
    page_count         = models.PositiveSmallIntegerField(default=1)
    language_detected  = models.CharField(max_length=10, blank=True)
    extracted_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ocr_result'

    def __str__(self):
        return f'OCRResult for {self.queue_item.file_name}'


class OCRExtractedEntity(models.Model):
    """Engineering entities parsed from OCR text."""

    class EntityType(models.TextChoices):
        DOCUMENT_NUMBER = 'DOC_NUM', 'Document Number'
        SPECIFICATION   = 'SPEC',    'Specification'
        STANDARD        = 'STD',     'Standard'
        DRAWING_NUMBER  = 'DWG',     'Drawing Number'
        PART_NUMBER     = 'PART',    'Part Number'
        DATE            = 'DATE',    'Date'
        OTHER           = 'OTHER',   'Other'

    result = models.ForeignKey(
        OCRResult, on_delete=models.CASCADE, related_name='entities',
    )
    entity_type  = models.CharField(max_length=20, choices=EntityType.choices)
    value        = models.CharField(max_length=500)
    confidence   = models.FloatField(null=True, blank=True)
    page_number  = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ocr_extracted_entity'
        indexes = [
            models.Index(fields=['entity_type', 'value']),
        ]

    def __str__(self):
        return f'{self.entity_type}: {self.value}'
