from django.contrib import admin
from apps.workflow.models import WorkType, Vendor, Tender, WorkLedger


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    search_fields = ['code', 'name']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    search_fields = ['code', 'name']


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ['tender_number', 'title', 'status', 'closing_date']
    list_filter = ['status']
    search_fields = ['tender_number', 'title', 'eoffice_file_number']


@admin.register(WorkLedger)
class WorkLedgerAdmin(admin.ModelAdmin):
    list_display = ['subject', 'work_type', 'section', 'status', 'received_date', 'closed_date']
    list_filter = ['status', 'section', 'work_type']
    search_fields = ['subject', 'eoffice_file_number', 'remarks']
    date_hierarchy = 'created_at'
