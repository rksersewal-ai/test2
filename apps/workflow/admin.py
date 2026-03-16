from django.contrib import admin
from apps.workflow.models import WorkType, WorkLedgerEntry


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    search_fields = ['code', 'name']


@admin.register(WorkLedgerEntry)
class WorkLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ['subject', 'work_type', 'section', 'status', 'received_date', 'closed_date']
    list_filter = ['status', 'section', 'work_type']
    search_fields = ['subject', 'eoffice_file_number', 'remarks']
    date_hierarchy = 'created_at'
