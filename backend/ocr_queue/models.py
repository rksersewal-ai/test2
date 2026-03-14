# =============================================================================
# FILE: backend/ocr_queue/models.py
# OCRJob — tracks document OCR text-extraction jobs
# =============================================================================
from django.db import models
from django.conf import settings


OCR_STATUS = [
    ('PENDING',    'Pending'),
    ('PROCESSING', 'Processing'),
    ('COMPLETED',  'Completed'),
    ('FAILED',     'Failed'),
]

OCR_ENGINES = [
    ('Tesseract', 'Tesseract OCR'),
    ('AzureOCR',  'Azure Computer Vision'),
    ('Paddle',    'PaddleOCR'),
    ('Manual',    'Manual Entry'),
]


class OCRJob(models.Model):
    document_id     = models.PositiveIntegerField(help_text='FK to documents.Document (kept loose)')
    document_title  = models.CharField(max_length=255, blank=True)
    file_name       = models.CharField(max_length=255, blank=True)
    engine          = models.CharField(max_length=20, choices=OCR_ENGINES, default='Tesseract')
    status          = models.CharField(max_length=20, choices=OCR_STATUS,  default='PENDING')
    page_count      = models.PositiveSmallIntegerField(null=True, blank=True)
    extracted_text  = models.TextField(blank=True)
    error_message   = models.TextField(blank=True)
    queued_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='ocr_jobs'
    )
    started_at      = models.DateTimeField(null=True, blank=True)
    completed_at    = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OCR Job'
        verbose_name_plural = 'OCR Jobs'

    def __str__(self):
        return f'OCRJob #{self.pk} [{self.status}] {self.document_title}'
