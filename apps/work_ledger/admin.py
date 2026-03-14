# =============================================================================
# FILE: apps/work_ledger/admin.py
# =============================================================================
from django.contrib import admin
from django.utils.html import format_html
from .models import WorkCategory, WorkEntry, WorkEntryAttachment, WorkVerification, WorkTarget


@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'work_type', 'is_active', 'sort_order']
    list_editable = ['is_active', 'sort_order']
    search_fields = ['code', 'name']
    list_filter   = ['work_type', 'is_active']


class WorkVerificationInline(admin.TabularInline):
    model          = WorkVerification
    extra          = 0
    readonly_fields = ['verifier', 'action', 'remarks', 'verified_at']
    can_delete     = False


class WorkEntryAttachmentInline(admin.TabularInline):
    model   = WorkEntryAttachment
    extra   = 0
    readonly_fields = ['file_name', 'file_size', 'uploaded_at']


@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):
    list_display   = [
        'id', 'user_link', 'work_date', 'work_type', 'priority',
        'reference_number', 'effort_summary', 'status_badge', 'created_at'
    ]
    list_filter    = ['status', 'work_type', 'priority', 'work_date']
    search_fields  = ['description', 'reference_number', 'user__first_name', 'user__last_name']
    date_hierarchy = 'work_date'
    readonly_fields = ['status', 'submitted_at', 'created_at', 'updated_at']
    inlines        = [WorkVerificationInline, WorkEntryAttachmentInline]
    list_per_page  = 50

    def user_link(self, obj):
        return format_html('<b>{}</b>', obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'Staff Member'

    def effort_summary(self, obj):
        if obj.effort_value:
            return f'{obj.effort_value} {obj.effort_unit}'
        return '—'
    effort_summary.short_description = 'Effort'

    def status_badge(self, obj):
        colours = {
            'DRAFT':     '#888',
            'SUBMITTED': '#1976D2',
            'VERIFIED':  '#388E3C',
            'RETURNED':  '#F57C00',
            'APPROVED':  '#2E7D32',
        }
        colour = colours.get(obj.status, '#333')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            colour, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(WorkTarget)
class WorkTargetAdmin(admin.ModelAdmin):
    list_display  = ['user', 'period_type', 'period_start', 'period_end',
                     'work_type', 'target_value', 'target_unit', 'is_active']
    list_filter   = ['period_type', 'work_type', 'is_active']
    search_fields = ['user__first_name', 'user__last_name']
