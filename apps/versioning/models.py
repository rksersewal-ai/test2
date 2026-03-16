# =============================================================================
# FILE: apps/versioning/models.py
# FR-006: Document Versioning
# Tracks document versions with delta diff, rollback support,
# version annotations, and 30-day soft-delete recovery.
# =============================================================================
import os
from django.db import models
from django.conf import settings
from apps.edms.models import Document


def version_upload_to(instance, filename):
    doc_num = instance.document.document_number.replace('/', '_')
    return os.path.join('versions', doc_num, f'v{instance.version_number}', filename)


class DocumentVersion(models.Model):
    """Stores a numbered version snapshot of a Document's file."""

    class VersionStatus(models.TextChoices):
        CURRENT    = 'CURRENT',    'Current'
        PREVIOUS   = 'PREVIOUS',   'Previous'
        ARCHIVED   = 'ARCHIVED',   'Archived'
        DELETED    = 'DELETED',    'Deleted (recoverable 30 days)'

    document         = models.ForeignKey(Document, on_delete=models.CASCADE,
                                         related_name='versions')
    version_number   = models.CharField(max_length=10,
                                        help_text='Semantic: 1.0, 1.1, 2.0 etc.')
    file_path        = models.FileField(upload_to=version_upload_to, max_length=600)
    file_size_bytes  = models.BigIntegerField(null=True, blank=True)
    checksum_sha256  = models.CharField(max_length=64, blank=True, db_index=True)
    status           = models.CharField(max_length=20,
                                        choices=VersionStatus.choices,
                                        default=VersionStatus.CURRENT)
    edit_summary     = models.TextField(blank=True)
    is_major         = models.BooleanField(default=False,
                                           help_text='True for major version (1.0 → 2.0)')
    created_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        on_delete=models.SET_NULL, related_name='versions_created'
    )
    created_at       = models.DateTimeField(auto_now_add=True)
    deleted_at       = models.DateTimeField(null=True, blank=True,
                                            help_text='Soft delete timestamp — recoverable for 30 days')

    class Meta:
        db_table        = 'ver_document_version'
        unique_together = [('document', 'version_number')]
        ordering        = ['document', '-created_at']

    def __str__(self):
        return f"{self.document.document_number} v{self.version_number} [{self.status}]"


class VersionAnnotation(models.Model):
    """User comments / annotations attached to a specific version."""

    version    = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE,
                                   related_name='annotations')
    text       = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT,
        related_name='version_annotations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ver_version_annotation'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.version}] {self.text[:80]}"


class VersionDiff(models.Model):
    """Stores the text diff between two consecutive versions (delta compression)."""

    from_version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE,
                                     related_name='diffs_as_source')
    to_version   = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE,
                                     related_name='diffs_as_target')
    diff_content = models.TextField(blank=True,
                                    help_text='Unified diff format or JSON delta')
    diff_size    = models.IntegerField(default=0, help_text='Bytes of diff')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'ver_version_diff'
        unique_together = [('from_version', 'to_version')]
        ordering        = ['-created_at']

    def __str__(self):
        return (
            f"{self.from_version.document.document_number}: "
            f"v{self.from_version.version_number} → v{self.to_version.version_number}"
        )
