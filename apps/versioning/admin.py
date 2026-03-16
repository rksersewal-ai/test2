from django.contrib import admin
from .models import DocumentVersion, AlterationHistory, VersionAnnotation, VersionDiff


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display    = ['document', 'version_number', 'status', 'is_major',
                       'file_size_bytes', 'created_by', 'created_at']
    list_filter     = ['status', 'is_major']
    search_fields   = ['document__document_number', 'version_number', 'checksum_sha256']
    readonly_fields = ['checksum_sha256', 'created_at', 'deleted_at']
    ordering        = ['-created_at']


@admin.register(AlterationHistory)
class AlterationHistoryAdmin(admin.ModelAdmin):
    list_display    = ['document', 'alteration_number', 'alteration_date',
                       'source_agency', 'implementation_status', 'implemented_at_plw']
    list_filter     = ['source_agency', 'implementation_status']
    search_fields   = ['document__document_number', 'alteration_number', 'source_reference']
    readonly_fields = ['created_at']
    ordering        = ['document', 'alteration_number']


@admin.register(VersionAnnotation)
class VersionAnnotationAdmin(admin.ModelAdmin):
    list_display    = ['version', 'text', 'created_by', 'created_at']
    search_fields   = ['version__document__document_number', 'text']
    readonly_fields = ['created_at']


@admin.register(VersionDiff)
class VersionDiffAdmin(admin.ModelAdmin):
    list_display    = ['from_version', 'to_version', 'diff_size', 'created_at']
    readonly_fields = ['diff_content', 'diff_size', 'created_at']
