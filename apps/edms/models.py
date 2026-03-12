"""EDMS models: Document, Revision, FileAttachment, Category."""
from django.db import models
from django.conf import settings
import os


class Category(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'edms_category'
        ordering = ['code']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.code} - {self.name}"


class DocumentType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'edms_document_type'

    def __str__(self):
        return self.name


class Document(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        SUPERSEDED = 'SUPERSEDED', 'Superseded'
        OBSOLETE = 'OBSOLETE', 'Obsolete'
        DRAFT = 'DRAFT', 'Draft'

    document_number = models.CharField(max_length=100, unique=True, db_index=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='documents')
    document_type = models.ForeignKey(DocumentType, null=True, blank=True, on_delete=models.SET_NULL, related_name='documents')
    section = models.ForeignKey('core.Section', null=True, blank=True, on_delete=models.SET_NULL, related_name='documents')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    source_standard = models.CharField(max_length=100, blank=True, help_text='e.g. RDSO, IRIS, DIN, IS, ABB')
    eoffice_file_number = models.CharField(max_length=100, blank=True, db_index=True)
    eoffice_subject = models.CharField(max_length=300, blank=True)
    keywords = models.TextField(blank=True, help_text='Comma-separated search keywords')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='documents_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'edms_document'
        ordering = ['document_number']

    def __str__(self):
        return f"{self.document_number} - {self.title}"


class Revision(models.Model):
    class Status(models.TextChoices):
        CURRENT = 'CURRENT', 'Current'
        SUPERSEDED = 'SUPERSEDED', 'Superseded'
        DRAFT = 'DRAFT', 'Draft'

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='revisions')
    revision_number = models.CharField(max_length=20)
    revision_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CURRENT)
    change_description = models.TextField(blank=True)
    prepared_by = models.CharField(max_length=150, blank=True)
    approved_by = models.CharField(max_length=150, blank=True)
    eoffice_ref = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='revisions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'edms_revision'
        unique_together = [('document', 'revision_number')]
        ordering = ['document', '-created_at']

    def __str__(self):
        return f"{self.document.document_number} Rev {self.revision_number}"


def upload_to(instance, filename):
    doc_num = instance.revision.document.document_number.replace('/', '_')
    rev = instance.revision.revision_number
    return os.path.join('documents', doc_num, f'rev_{rev}', filename)


class FileAttachment(models.Model):
    class FileType(models.TextChoices):
        PDF = 'PDF', 'PDF'
        IMAGE = 'IMAGE', 'Image'
        TIFF = 'TIFF', 'TIFF'

    revision = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to=upload_to, max_length=500)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=10, choices=FileType.choices, default=FileType.PDF)
    page_count = models.IntegerField(null=True, blank=True)
    checksum_sha256 = models.CharField(max_length=64, blank=True, db_index=True)
    is_primary = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='files_uploaded')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'edms_file_attachment'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.file_name
