# =============================================================================
# FILE: apps/sdr/admin.py
# =============================================================================
from django.contrib  import admin
from django.utils.html import format_html
from .models import SDRRecord, SDRItem


class SDRItemInline(admin.TabularInline):
    model   = SDRItem
    extra   = 1
    fields  = [
        'document_type',
        'drawing',
        'specification',
        'document_number',
        'document_title',
        'alteration_no',
        'size',
        'copies',
        'controlled_copy',
    ]
    readonly_fields = ['document_number', 'document_title', 'alteration_no']
    autocomplete_fields = ['drawing', 'specification']


@admin.register(SDRRecord)
class SDRRecordAdmin(admin.ModelAdmin):
    list_display = [
        'sdr_number',
        'issue_date',
        'shop_name',
        'requesting_official',
        'issuing_official',
        'receiving_official',
        'total_items',
        'controlled_badge',
        'created_at',
    ]
    search_fields  = [
        'sdr_number', 'shop_name',
        'requesting_official', 'receiving_official',
        'issuing_official',
        'items__document_number',
    ]
    list_filter    = ['shop_name', 'issuing_official', 'issue_date']
    date_hierarchy = 'issue_date'
    ordering       = ['-issue_date']
    readonly_fields = ['sdr_number', 'created_by', 'created_at', 'updated_at']
    inlines        = [SDRItemInline]

    fieldsets = [
        ('Register Details', {'fields': [
            'sdr_number',
            'issue_date',
        ]}),
        ('Parties', {'fields': [
            'shop_name',
            'requesting_official',
            'issuing_official',
            'receiving_official',
        ]}),
        ('Remarks', {'fields': ['remarks']}),
        ('Audit', {'fields': ['created_by', 'created_at', 'updated_at'],
                   'classes': ['collapse']}),
    ]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='Items')
    def total_items(self, obj):
        return obj.items.count()

    @admin.display(description='Controlled?')
    def controlled_badge(self, obj):
        if obj.items.filter(controlled_copy=True).exists():
            return format_html(
                '<span style="background:#003366;color:white;padding:2px 8px;'
                'border-radius:4px;font-size:11px;font-weight:bold">YES</span>'
            )
        return format_html('<span style="color:#999">—</span>')
