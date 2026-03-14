# =============================================================================
# FILE: backend/master/models_tech_eval.py
# MODEL: PLTechEvalDocument
#
# Stores up to 3 technical evaluation documents per PL number.
# Each record links a tender number + evaluation year to a stored file
# (PDF or DOCX) for reference in future evaluation cases.
# =============================================================================
import os
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


def _eval_doc_upload_path(instance, filename):
    """Store under media/pl_eval_docs/{pl_number}/{filename}"""
    return os.path.join('pl_eval_docs', instance.pl_number, filename)


def _validate_eval_doc_format(file):
    """Accept only PDF and DOCX."""
    name = getattr(file, 'name', '') or ''
    ext  = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    if ext not in ('pdf', 'docx'):
        raise ValidationError(
            'Only PDF (.pdf) and Word (.docx) files are accepted for '
            'technical evaluation documents.'
        )


def _validate_max_three(pl_number, instance_pk=None):
    """Enforce maximum 3 documents per PL number."""
    qs = PLTechEvalDocument.objects.filter(pl_number=pl_number)
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    if qs.count() >= 3:
        raise ValidationError(
            'Maximum 3 technical evaluation documents are allowed per PL number. '
            'Delete an existing document before uploading a new one.'
        )


class PLTechEvalDocument(models.Model):
    """
    Technical evaluation document for a PL number.
    Limited to 3 per PL — oldest should be deleted when adding a 4th.
    """
    pl_number     = models.CharField(max_length=50, db_index=True)
    tender_number = models.CharField(max_length=100)
    eval_year     = models.PositiveSmallIntegerField()
    document_file = models.FileField(
        upload_to=_eval_doc_upload_path,
        validators=[_validate_eval_doc_format],
    )
    file_name     = models.CharField(max_length=255, editable=False)
    file_format   = models.CharField(
        max_length=4,
        choices=[('PDF', 'PDF'), ('DOCX', 'DOCX')],
        editable=False,
    )
    file_size_kb  = models.PositiveIntegerField(editable=False, default=0)
    uploaded_by   = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='uploaded_eval_docs',
    )
    uploaded_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label         = 'master'
        ordering          = ['-uploaded_at']
        verbose_name      = 'PL Technical Evaluation Document'
        verbose_name_plural = 'PL Technical Evaluation Documents'
        indexes = [
            models.Index(fields=['pl_number', '-uploaded_at']),
        ]

    def __str__(self):
        return f'{self.pl_number} | {self.tender_number} ({self.eval_year}) | {self.file_name}'

    def save(self, *args, **kwargs):
        # Validate max 3 on create
        if not self.pk:
            _validate_max_three(self.pl_number)

        # Derive file metadata from the uploaded file
        if self.document_file:
            raw_name = getattr(self.document_file, 'name', '') or ''
            # Strip path — keep only the filename part
            self.file_name   = os.path.basename(raw_name)
            ext              = self.file_name.rsplit('.', 1)[-1].lower() if '.' in self.file_name else ''
            self.file_format = 'PDF' if ext == 'pdf' else 'DOCX'
            size = getattr(self.document_file, 'size', 0) or 0
            self.file_size_kb = max(1, round(size / 1024))

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Remove physical file from disk when record is deleted."""
        storage = self.document_file.storage
        path    = self.document_file.name
        super().delete(*args, **kwargs)
        try:
            if path and storage.exists(path):
                storage.delete(path)
        except Exception:
            pass  # Don't crash if file already gone
