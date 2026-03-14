# =============================================================================
# FILE: apps/pdf_tools/models.py
# SPRINT 6 — PdfJob: tracks every merge/split/rotate/extract operation
# =============================================================================
from django.db import models
from django.conf import settings


class PdfJob(models.Model):
    class Operation(models.TextChoices):
        MERGE   = 'MERGE',   'Merge'
        SPLIT   = 'SPLIT',   'Split'
        ROTATE  = 'ROTATE',  'Rotate'
        EXTRACT = 'EXTRACT', 'Extract Pages'

    class JobStatus(models.TextChoices):
        QUEUED    = 'QUEUED',    'Queued'
        RUNNING   = 'RUNNING',   'Running'
        DONE      = 'DONE',      'Done'
        FAILED    = 'FAILED',    'Failed'

    operation      = models.CharField(max_length=10, choices=Operation.choices)
    status         = models.CharField(
        max_length=10, choices=JobStatus.choices, default=JobStatus.QUEUED
    )
    # Input: JSON list of MEDIA_ROOT-relative paths
    input_files    = models.JSONField(default=list)
    # Params: page_ranges, pages_per_chunk, angle, page_numbers, output_name
    params         = models.JSONField(default=dict)
    # Output: single path or list of paths
    output_files   = models.JSONField(default=list)
    error_message  = models.TextField(blank=True)
    created_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pdf_jobs'
    )
    created_at     = models.DateTimeField(auto_now_add=True)
    completed_at   = models.DateTimeField(null=True, blank=True)
    # Optional: link result back to an EDMS revision
    linked_revision = models.ForeignKey(
        'edms.Revision', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pdf_jobs'
    )

    class Meta:
        db_table = 'pdf_job'
        ordering = ['-created_at']

    def __str__(self):
        return f'PdfJob #{self.pk} [{self.operation}] {self.status}'
