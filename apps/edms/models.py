# =============================================================================
# FILE: apps/edms/models.py
# FIX #11: Corrected db_table naming for Correspondent and
#          DocumentCorrespondentLink and DocumentNote to use
#          consistent 'edms_' prefix, matching all other EDMS models.
#          Previous: 'correspondent', 'document_correspondent_link',
#                    'document_note' (missing edms_ prefix)
#          Fixed:    'edms_correspondent', 'edms_document_correspondent_link',
#                    'edms_document_note'
# NOTE: If you have already run SQL migrations with old table names,
#       run: sql/FIX_011_rename_tables.sql before applying Django migrations.
# =============================================================================
from django.db import models
from django.conf import settings
import os


class Category(models.Model):
    code        = models.CharField(max_length=20, unique=True)
    name        = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='children')
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table            = 'edms_category'
        ordering            = ['code']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.code} - {self.name}"


class DocumentType(models.Model):
    code        = models.CharField(max_length=20, unique=True)
    name        = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'edms_document_type'

    def __str__(self):
        return self.name


class Document(models.Model):
    class Status(models.TextChoices):
        ACTIVE     = 'ACTIVE',     'Active'
        SUPERSEDED = 'SUPERSEDED', 'Superseded'
        OBSOLETE   = 'OBSOLETE',   'Obsolete'
        DRAFT      = 'DRAFT',      'Draft'

    document_number     = models.CharField(max_length=100, unique=True, db_index=True)
    title               = models.CharField(max_length=300)
    description         = models.TextField(blank=True)
    category            = models.ForeignKey(Category, null=True, blank=True,
                                            on_delete=models.SET_NULL, related_name='documents')
    document_type       = models.ForeignKey(DocumentType, null=True, blank=True,
                                            on_delete=models.SET_NULL, related_name='documents')
    section             = models.ForeignKey('core.Section', null=True, blank=True,
                                            on_delete=models.SET_NULL, related_name='documents')
    status              = models.CharField(max_length=20, choices=Status.choices,
                                           default=Status.ACTIVE)
    source_standard     = models.CharField(max_length=100, blank=True)
    eoffice_file_number = models.CharField(max_length=100, blank=True, db_index=True)
    eoffice_subject     = models.CharField(max_length=300, blank=True)
    keywords            = models.TextField(blank=True)
    created_by          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                            on_delete=models.SET_NULL,
                                            related_name='documents_created')
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'edms_document'
        ordering = ['document_number']

    def __str__(self):
        return f"{self.document_number} - {self.title}"


class Revision(models.Model):
    class Status(models.TextChoices):
        CURRENT    = 'CURRENT',    'Current'
        SUPERSEDED = 'SUPERSEDED', 'Superseded'
        DRAFT      = 'DRAFT',      'Draft'

    document           = models.ForeignKey(Document, on_delete=models.CASCADE,
                                           related_name='revisions')
    revision_number    = models.CharField(max_length=20)
    revision_date      = models.DateField(null=True, blank=True)
    status             = models.CharField(max_length=20, choices=Status.choices,
                                          default=Status.CURRENT)
    change_description = models.TextField(blank=True)
    prepared_by        = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='revisions_prepared'
    )
    approved_by        = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='revisions_approved'
    )
    eoffice_ref = models.CharField(max_length=100, blank=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        on_delete=models.SET_NULL, related_name='revisions_created'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'edms_revision'
        unique_together = [('document', 'revision_number')]
        ordering        = ['document', '-created_at']

    def __str__(self):
        return f"{self.document.document_number} Rev {self.revision_number}"


def upload_to(instance, filename):
    doc_num = instance.revision.document.document_number.replace('/', '_')
    rev     = instance.revision.revision_number
    return os.path.join('documents', doc_num, f'rev_{rev}', filename)


class FileAttachment(models.Model):
    class FileType(models.TextChoices):
        PDF   = 'PDF',   'PDF'
        IMAGE = 'IMAGE', 'Image'
        TIFF  = 'TIFF',  'TIFF'

    revision        = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name='files')
    file_name       = models.CharField(max_length=255)
    file_path       = models.FileField(upload_to=upload_to, max_length=500)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    file_type       = models.CharField(max_length=10, choices=FileType.choices,
                                       default=FileType.PDF)
    page_count      = models.IntegerField(null=True, blank=True)
    checksum_sha256 = models.CharField(max_length=64, blank=True, db_index=True)
    is_primary      = models.BooleanField(default=False)
    uploaded_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        on_delete=models.SET_NULL, related_name='files_uploaded'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'edms_file_attachment'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.file_name


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #9: Custom Fields
# ---------------------------------------------------------------------------

class CustomFieldDefinition(models.Model):
    class FieldType(models.TextChoices):
        TEXT    = 'text',    'Text'
        NUMBER  = 'number',  'Number'
        DATE    = 'date',    'Date'
        SELECT  = 'select',  'Select (dropdown)'
        BOOLEAN = 'boolean', 'Yes / No'

    document_type  = models.ForeignKey(DocumentType, on_delete=models.CASCADE,
                                       related_name='custom_field_definitions')
    field_name     = models.CharField(max_length=80)
    field_label    = models.CharField(max_length=200)
    field_type     = models.CharField(max_length=20, choices=FieldType.choices,
                                      default=FieldType.TEXT)
    select_options = models.TextField(blank=True)
    is_required    = models.BooleanField(default=False)
    sort_order     = models.IntegerField(default=0)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'edms_custom_field_definition'
        unique_together = [('document_type', 'field_name')]
        ordering        = ['document_type', 'sort_order', 'field_name']

    def __str__(self):
        return f"{self.document_type.name} / {self.field_label}"

    def get_select_options_list(self) -> list[str]:
        if self.field_type == self.FieldType.SELECT and self.select_options:
            return [o.strip() for o in self.select_options.split(',') if o.strip()]
        return []


class DocumentCustomField(models.Model):
    document    = models.ForeignKey(Document, on_delete=models.CASCADE,
                                    related_name='custom_fields')
    definition  = models.ForeignKey(CustomFieldDefinition, on_delete=models.RESTRICT,
                                    related_name='values')
    field_value = models.TextField(blank=True, null=True)
    updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name='custom_fields_updated')
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'edms_document_custom_field'
        unique_together = [('document', 'definition')]
        ordering        = ['definition__sort_order']

    def __str__(self):
        return f"{self.document.document_number} / {self.definition.field_label} = {self.field_value}"


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #14: Correspondent Tracking
# ---------------------------------------------------------------------------

class Correspondent(models.Model):
    class OrgType(models.TextChoices):
        RDSO       = 'RDSO',       'RDSO'
        CLW        = 'CLW',        'CLW'
        BLW        = 'BLW',        'BLW'
        ICF        = 'ICF',        'ICF'
        ZR         = 'ZR',         'Zonal Railway'
        HQ         = 'HQ',         'Railway Board / HQ'
        VENDOR     = 'VENDOR',     'Vendor / Supplier'
        CONTRACTOR = 'CONTRACTOR', 'Contractor'
        OTHER      = 'OTHER',      'Other'

    name       = models.CharField(max_length=300)
    short_code = models.CharField(max_length=30, unique=True)
    org_type   = models.CharField(max_length=20, choices=OrgType.choices, default=OrgType.OTHER)
    address    = models.TextField(blank=True)
    email      = models.EmailField(blank=True)
    is_active  = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='correspondents_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # FIX #11: was 'correspondent' (missing edms_ prefix)
        db_table = 'edms_correspondent'
        ordering = ['name']

    def __str__(self):
        return f"{self.short_code} — {self.name}"


class DocumentCorrespondentLink(models.Model):
    class LinkType(models.TextChoices):
        ISSUED_BY    = 'ISSUED_BY',    'Issued By'
        ADDRESSED_TO = 'ADDRESSED_TO', 'Addressed To'
        CC           = 'CC',           'CC'
        APPROVED_BY  = 'APPROVED_BY',  'Approved By'
        CONSULTED    = 'CONSULTED',    'Consulted'

    document         = models.ForeignKey(Document, on_delete=models.CASCADE,
                                         related_name='correspondent_links')
    correspondent    = models.ForeignKey(Correspondent, on_delete=models.RESTRICT,
                                         related_name='document_links')
    reference_number = models.CharField(max_length=200, blank=True)
    reference_date   = models.DateField(null=True, blank=True)
    link_type        = models.CharField(max_length=20, choices=LinkType.choices,
                                        default=LinkType.ISSUED_BY)
    remarks    = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='correspondent_links_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # FIX #11: was 'document_correspondent_link'
        db_table = 'edms_document_correspondent_link'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.document.document_number} ← "
            f"{self.correspondent.short_code} ({self.link_type})"
        )


# ---------------------------------------------------------------------------
# SPRINT 1 — Feature #12: Document Notes & Annotations
# ---------------------------------------------------------------------------

class DocumentNote(models.Model):
    class NoteType(models.TextChoices):
        REVIEW          = 'REVIEW',          'Review Comment'
        QUERY           = 'QUERY',           'Query'
        OBSERVATION     = 'OBSERVATION',     'Observation'
        INFO            = 'INFO',            'Information'
        ACTION_REQUIRED = 'ACTION_REQUIRED', 'Action Required'

    document        = models.ForeignKey(Document, on_delete=models.CASCADE,
                                        related_name='notes')
    revision        = models.ForeignKey(Revision, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='notes')
    note_type       = models.CharField(max_length=20, choices=NoteType.choices,
                                       default=NoteType.OBSERVATION)
    note_text       = models.TextField()
    is_resolved     = models.BooleanField(default=False)
    resolved_by     = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='notes_resolved')
    resolved_at     = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                        on_delete=models.RESTRICT, related_name='notes_created')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        # FIX #11: was 'document_note'
        db_table = 'edms_document_note'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.note_type}] {self.document.document_number} — {self.note_text[:60]}"
