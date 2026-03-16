from django.contrib import admin
from .models import DocumentVersion, VersionAnnotation, VersionDiff


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display  = ['document', 'version_number', 'status', 'is_major', 'file_size_bytes', 'created_by', 'created_at']
    list_filter   = ['status', 'is_major']
    search_fields = ['document__document_number', 'version_number', 'checksum_sha256']
    readonly_fields = ['checksum_sha256', 'created_at', 'deleted_at']
    ordering      = ['-created_at']


@admin.register(VersionAnnotation)
class VersionAnnotationAdmin(admin.ModelAdmin):
    list_display  = ['version', 'text', 'created_by', 'created_at']
    search_fields = ['version__document__document_number', 'text']
    readonly_fields = ['created_at']


@admin.register(VersionDiff)
class VersionDiffAdmin(admin.ModelAdmin):
    list_display  = ['from_version', 'to_version', 'diff_size', 'created_at']
    readonly_fields = ['diff_content', 'diff_size', 'created_at']
