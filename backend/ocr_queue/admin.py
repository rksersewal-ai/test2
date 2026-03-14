from django.contrib import admin
from .models import OCRJob


@admin.register(OCRJob)
class OCRJobAdmin(admin.ModelAdmin):
    list_display   = ['id', 'document_title', 'file_name', 'engine', 'status', 'page_count', 'created_at', 'completed_at']
    list_filter    = ['status', 'engine']
    search_fields  = ['document_title', 'file_name']
    ordering       = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at', 'error_message']
