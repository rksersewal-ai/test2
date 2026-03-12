from django.contrib import admin
from apps.edms.models import Document, Revision, FileAttachment, Category, DocumentType


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'is_active']
    search_fields = ['code', 'name']


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']


class RevisionInline(admin.TabularInline):
    model = Revision
    extra = 0
    fields = ['revision_number', 'revision_date', 'status', 'prepared_by']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'title', 'category', 'section', 'status', 'created_at']
    search_fields = ['document_number', 'title', 'eoffice_file_number', 'keywords']
    list_filter = ['status', 'category', 'section', 'source_standard']
    inlines = [RevisionInline]


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ['document', 'revision_number', 'revision_date', 'status']
    list_filter = ['status']


@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'revision', 'file_type', 'file_size_bytes', 'uploaded_at']
    search_fields = ['file_name', 'checksum_sha256']
