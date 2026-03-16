# =============================================================================
# FILE: apps/versioning/models.py
# FR-006: Document Versioning — Amended PRD v1.0
# PRD Sections 5.2.4, 7.3, 8.4, 13.9 (alterationhistory table)
# Handles: automatic version numbering, previous versions retained,
# version comparison, rollback with approval, version history audit.
# Tables: ver_document_version, ver_alteration_history,
#         ver_version_annotation, ver_version_diff
# =============================================================================
import os
from django.db import models
from django.conf import settings
from apps.edms.models import Document


def version_upload_to(instance, filename):
    doc_num = instance.document.document_number.replace('/', '_')
    return os.path.join('versions', doc_num, f'v{instance.version_number}', filename)


class DocumentVersion(models.Model):
    """Stores a numbered semantic version snapshot of a Document file.

    PRD 5.2.4: Version Control — automatic version numbering,
    previous versions retained and accessible, rollback to previous version.
    """

    class VersionStatus(models.TextChoices):
        CURRENT  = 'CURRENT',  'Current'
        PREVIOUS = 'PREVIOUS', 'Previous'
        ARCHIVED = 'ARCHIVED', 'Archived'
        DELETED  = 'DELETED',  'Deleted (recoverable 30 days)'

    document        = models.ForeignKey(Document, on_delete=models.CASCADE,
                                        related_name='versions')
    version_number  = models.CharField(max_length=10,
                                       help_text='Semantic: 1.0, 1.1, 2.0 etc.')
    file_path       = models.FileField(upload_to=version_upload_to, max_length=600)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    checksum_sha256 = models.CharField(max_length=64, blank=True, db_index=True)
    status          = models.CharField(max_length=20, choices=VersionStatus.choices,
                                       default=VersionStatus.CURRENT)
    edit_summary    = models.TextField(blank=True)
    is_major        = models.BooleanField(default=False)
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                        on_delete=models.SET_NULL,
                                        related_name='versions_created')
    created_at      = models.DateTimeField(auto_now_add=True)
    deleted_at      = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table        = 'ver_document_version'
        unique_together = [('document', 'version_number')]
        ordering        = ['document', '-created_at']

    def __str__(self):
        return f"{self.document.document_number} v{self.version_number} [{self.status}]"


class AlterationHistory(models.Model):
    """Records full alteration history per document version.

    PRD Table 13.9: alterationhistory — tracks every revision/alteration
    with description, reason, probable impacts, source agency, file hashes,
    and implementation status. Matches drawing revision record in PRD 7.3.
    """

    class ImplementationStatus(models.TextChoices):
        PENDING     = 'PENDING',     'Pending'
        IMPLEMENTED = 'IMPLEMENTED', 'Implemented'
        NA          = 'NA',          'Not Applicable'

    document              = models.ForeignKey(Document, on_delete=models.CASCADE,
                                              related_name='alteration_history')
    version               = models.ForeignKey(DocumentVersion, on_delete=models.SET_NULL,
                                              null=True, blank=True,
                                              related_name='alterations')
    alteration_number     = models.CharField(max_length=20,
                                             help_text='00, 01, 02 … as per CLW convention')
    previous_alteration   = models.CharField(max_length=20, blank=True)
    alteration_date       = models.DateField(null=True, blank=True)
    changes_description   = models.TextField(blank=True)
    change_reason         = models.TextField(blank=True)
    probable_impacts      = models.TextField(blank=True)
    source_agency         = models.CharField(max_length=10, blank=True,
                                             help_text='CLW/BLW/RDSO/ICF/PLW')
    source_reference      = models.CharField(max_length=200, blank=True)
    source_date           = models.DateField(null=True, blank=True)
    affected_pl_numbers   = models.TextField(blank=True,
                                             help_text='Comma-separated PL numbers affected')
    implementation_status = models.CharField(
        max_length=20, choices=ImplementationStatus.choices,
        default=ImplementationStatus.PENDING
    )
    implemented_at_plw    = models.DateField(null=True, blank=True)
    implemented_by        = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                              on_delete=models.SET_NULL,
                                              related_name='alterations_implemented')
    file_path_old         = models.CharField(max_length=500, blank=True)
    file_path_new         = models.CharField(max_length=500, blank=True)
    created_at            = models.DateTimeField(auto_now_add=True)
    created_by            = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                              on_delete=models.SET_NULL,
                                              related_name='alterations_created')

    class Meta:
        db_table        = 'ver_alteration_history'
        unique_together = [('document', 'alteration_number')]
        ordering        = ['document', 'alteration_number']

    def __str__(self):
        return (
            f"{self.document.document_number} — Alt {self.alteration_number} "
            f"({self.alteration_date}) [{self.implementation_status}]"
        )


class VersionAnnotation(models.Model):
    """User comments / annotations attached to a specific version."""

    version    = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE,
                                   related_name='annotations')
    text       = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT,
                                   related_name='version_annotations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ver_version_annotation'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.version}] {self.text[:80]}"


class VersionDiff(models.Model):
    """Stores diff between two consecutive versions (delta storage)."""

    from_version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE,
                                     related_name='diffs_as_source')
    to_version   = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE,
                                     related_name='diffs_as_target')
    diff_content = models.TextField(blank=True)
    diff_size    = models.IntegerField(default=0)
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
