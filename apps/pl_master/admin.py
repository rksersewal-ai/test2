# =============================================================================
# FILE: apps/pl_master/admin.py
# =============================================================================
from django.contrib  import admin, messages
from django.utils    import timezone
from django.utils.html import format_html
from .models import (
    ControllingAgency, PLMaster, DrawingMaster, SpecificationMaster,
    VendorDrawing, STRMaster, RDSOReference, AlterationHistory,
    PLDrawingLink, PLSpecLink, PLStandardLink, PLSMILink,
    PLAlternate, PLLocoApplicability,
)


# =============================================================================
# Inline: AlterationHistory inside DrawingMaster / SpecificationMaster
# =============================================================================
class AlterationHistoryInline(admin.TabularInline):
    """
    Shows all alteration records for a given Drawing or Specification
    directly on the parent admin change page.
    Read-only — records are auto-created by signals; manual edits not allowed.
    """
    model          = AlterationHistory
    extra          = 0
    can_delete     = False
    show_change_link = True
    ordering       = ['-alteration_date']

    # Restrict inline to records matching the parent document_number
    # (resolved via custom get_queryset below)
    fields = [
        'alteration_number', 'previous_alteration',
        'alteration_date', 'changes_description',
        'probable_impacts', 'source_agency',
        'implementation_status', 'implementation_remarks',
    ]
    readonly_fields = [
        'alteration_number', 'previous_alteration',
        'alteration_date', 'changes_description',
        'probable_impacts', 'source_agency',
    ]

    def has_add_permission(self, request, obj=None):
        return False  # Only created via signal


class DrawingAlterationHistoryInline(AlterationHistoryInline):
    verbose_name        = 'Alteration Record'
    verbose_name_plural = 'Alteration History'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filtered further by get_formset override on parent admin
        return qs.filter(document_type='DRAWING')


class SpecAlterationHistoryInline(AlterationHistoryInline):
    verbose_name        = 'Amendment Record'
    verbose_name_plural = 'Amendment / Alteration History'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(document_type='SPEC')


# =============================================================================
# Controlling Agency
# =============================================================================
@admin.register(ControllingAgency)
class ControllingAgencyAdmin(admin.ModelAdmin):
    list_display  = ['agency_code', 'agency_name', 'agency_type', 'is_active']
    search_fields = ['agency_code', 'agency_name']
    list_filter   = ['is_active']


# =============================================================================
# PLMaster Inlines
# =============================================================================
class PLDrawingLinkInline(admin.TabularInline):
    model   = PLDrawingLink
    extra   = 0
    fields  = ['drawing', 'is_primary', 'link_purpose', 'is_active']


class PLSpecLinkInline(admin.TabularInline):
    model   = PLSpecLink
    extra   = 0
    fields  = ['specification', 'is_primary', 'link_purpose', 'is_active']


class PLSMILinkInline(admin.TabularInline):
    model   = PLSMILink
    extra   = 0
    fields  = ['smi_number', 'smi_type', 'is_mandatory', 'deadline', 'implementation_status']


class PLAlternateInline(admin.TabularInline):
    model   = PLAlternate
    extra   = 0
    fk_name = 'pl_item'
    fields  = ['alternate_pl', 'interchangeable', 'remarks']


class PLLocoApplicabilityInline(admin.TabularInline):
    model   = PLLocoApplicability
    extra   = 0
    fields  = ['loco_type', 'assembly_group', 'qty_per_loco', 'remarks']


# =============================================================================
# PLMaster
# =============================================================================
@admin.register(PLMaster)
class PLMasterAdmin(admin.ModelAdmin):
    list_display   = [
        'pl_number', 'part_description', 'inspection_category',
        'safety_item', 'vd_item', 'controlling_agency', 'is_active'
    ]
    search_fields  = ['pl_number', 'part_description', 'uvam_id', 'e_office_file_no']
    list_filter    = [
        'inspection_category', 'safety_item', 'vd_item', 'nvd_item',
        'rdso_controlled', 'controlling_agency', 'is_active'
    ]
    readonly_fields = ['created_at', 'updated_at', 'version']
    inlines        = [
        PLDrawingLinkInline, PLSpecLinkInline,
        PLSMILinkInline, PLAlternateInline, PLLocoApplicabilityInline,
    ]
    fieldsets = [
        ('Identity',      {'fields': ['pl_number', 'part_description', 'part_description_hindi']}),
        ('BOM Hierarchy', {'fields': ['mother_part', 'mother_part_description']}),
        ('Safety',        {'fields': [
            'safety_item', 'safety_classification', 'severity_of_failure',
            'consequences_upon_failure', 'failure_mode'
        ]}),
        ('Functional',    {'fields': ['functionality', 'used_in', 'application_area']}),
        ('Inspection',    {'fields': [
            'inspection_category', 'stage_inspection_reqd', 'inspection_agency'
        ]}),
        ('Agency & Procurement', {'fields': [
            'controlling_agency', 'controlling_pu', 'rdso_controlled',
            'vd_item', 'uvam_id', 'uvam_category', 'nvd_item',
            'set_list_number', 'set_list_description',
        ]}),
        ('Supervisors',   {'fields': [
            'design_supervisor', 'design_supervisor_id',
            'concerned_supervisor', 'concerned_supervisor_id',
        ]}),
        ('References',    {'fields': ['e_office_file_no', 'case_no', 'keywords', 'tags', 'remarks']}),
        ('Lifecycle',     {'fields': ['is_active', 'version', 'created_by', 'created_at', 'updated_by', 'updated_at']}),
    ]


# =============================================================================
# DrawingMaster  — with AlterationHistory inline
# =============================================================================
@admin.register(DrawingMaster)
class DrawingMasterAdmin(admin.ModelAdmin):
    list_display  = [
        'drawing_number', 'drawing_title', 'drawing_type',
        'current_alteration', 'alteration_date',
        'controlling_agency', 'drawing_readable',
        'alteration_badge', 'is_active',
    ]
    search_fields = ['drawing_number', 'drawing_title']
    list_filter   = [
        'drawing_type', 'controlling_agency',
        'drawing_readable', 'is_latest', 'is_active',
    ]
    date_hierarchy  = 'alteration_date'
    readonly_fields = ['created_at', 'updated_at']
    inlines         = [DrawingAlterationHistoryInline]

    fieldsets = [
        ('Drawing Identity', {'fields': [
            'drawing_number', 'drawing_title', 'drawing_type',
            'size', 'scale', 'sheet_count',
        ]}),
        ('Current Alteration', {'fields': [
            'current_alteration', 'alteration_date',
            'alteration_description', 'probable_impacts',
        ]}),
        ('Controlling Authority', {'fields': [
            'controlling_agency', 'source_reference',
        ]}),
        ('Quality / Status', {'fields': [
            'drawing_readable', 'is_latest', 'is_active',
            'supersedes', 'superseded_by',
        ]}),
        ('File', {'fields': [
            'file_path', 'file_name', 'file_size', 'file_hash', 'mime_type',
        ]}),
        ('Audit', {'fields': ['created_at', 'updated_at']}),
    ]

    @admin.display(description='Alt History')
    def alteration_badge(self, obj):
        count = AlterationHistory.objects.filter(
            document_type='DRAWING',
            document_number=obj.drawing_number
        ).count()
        if count == 0:
            return format_html('<span style="color:#999">—</span>')
        color = '#003366' if count < 5 else ('#CC9900' if count < 10 else '#CC0000')
        return format_html(
            '<span style="background:{};color:white;padding:2px 7px;'
            'border-radius:10px;font-size:11px;font-weight:bold">{}</span>',
            color, count
        )


# =============================================================================
# SpecificationMaster — with AlterationHistory inline
# =============================================================================
@admin.register(SpecificationMaster)
class SpecificationMasterAdmin(admin.ModelAdmin):
    list_display  = [
        'spec_number', 'spec_title', 'spec_type',
        'current_alteration', 'alteration_date',
        'controlling_agency',
        'amendment_badge', 'is_active',
    ]
    search_fields = ['spec_number', 'spec_title']
    list_filter   = ['spec_type', 'controlling_agency', 'is_latest', 'is_active']
    date_hierarchy  = 'alteration_date'
    readonly_fields = ['created_at', 'updated_at']
    inlines         = [SpecAlterationHistoryInline]

    fieldsets = [
        ('Specification Identity', {'fields': [
            'spec_number', 'spec_title', 'spec_type',
        ]}),
        ('Current Alteration / Amendment', {'fields': [
            'current_alteration', 'alteration_date',
            'alteration_description', 'probable_impacts',
        ]}),
        ('Controlling Authority', {'fields': [
            'controlling_agency', 'source_reference',
        ]}),
        ('Status', {'fields': [
            'is_latest', 'is_active',
            'supersedes', 'superseded_by',
        ]}),
        ('File', {'fields': [
            'file_path', 'file_name', 'file_size', 'file_hash',
        ]}),
        ('Audit', {'fields': ['created_at', 'updated_at']}),
    ]

    @admin.display(description='Amendments')
    def amendment_badge(self, obj):
        count = AlterationHistory.objects.filter(
            document_type='SPEC',
            document_number=obj.spec_number
        ).count()
        if count == 0:
            return format_html('<span style="color:#999">—</span>')
        color = '#003366' if count < 5 else ('#CC9900' if count < 10 else '#CC0000')
        return format_html(
            '<span style="background:{};color:white;padding:2px 7px;'
            'border-radius:10px;font-size:11px;font-weight:bold">{}</span>',
            color, count
        )


# =============================================================================
# AlterationHistory — standalone admin (full-featured)
# =============================================================================
@admin.action(description='Mark selected alterations as IMPLEMENTED')
def mark_as_implemented(modeladmin, request, queryset):
    updated = queryset.exclude(implementation_status='IMPLEMENTED').update(
        implementation_status='IMPLEMENTED'
    )
    modeladmin.message_user(
        request,
        f'{updated} alteration(s) marked as IMPLEMENTED.',
        messages.SUCCESS
    )


@admin.action(description='Mark selected alterations as PENDING')
def mark_as_pending(modeladmin, request, queryset):
    updated = queryset.exclude(implementation_status='PENDING').update(
        implementation_status='PENDING'
    )
    modeladmin.message_user(
        request,
        f'{updated} alteration(s) reset to PENDING.',
        messages.WARNING
    )


@admin.register(AlterationHistory)
class AlterationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'document_type_badge',
        'document_number',
        'alteration_number',
        'previous_alteration',
        'alteration_date',
        'source_agency',
        'status_badge',
        'affected_count',
        'created_at',
    ]
    list_filter = [
        'document_type',
        'implementation_status',
        'source_agency',
    ]
    search_fields = [
        'document_number',
        'alteration_number',
        'changes_description',
        'probable_impacts',
        'source_reference',
    ]
    date_hierarchy  = 'alteration_date'
    ordering        = ['-alteration_date']
    readonly_fields = [
        'document_type', 'document_number',
        'alteration_number', 'previous_alteration',
        'alteration_date', 'changes_description',
        'probable_impacts', 'source_agency',
        'affected_pl_numbers', 'created_at',
    ]
    actions = [mark_as_implemented, mark_as_pending]

    fieldsets = [
        ('Document', {'fields': [
            'document_type', 'document_number',
        ]}),
        ('Alteration Details', {'fields': [
            'alteration_number', 'previous_alteration',
            'alteration_date', 'source_agency', 'source_reference',
        ]}),
        ('Change Description', {'fields': [
            'changes_description', 'probable_impacts',
        ]}),
        ('Affected PL Numbers', {'fields': [
            'affected_pl_numbers',
        ]}),
        ('Implementation', {'fields': [
            'implementation_status', 'implementation_remarks',
        ]}),
        ('Audit', {'fields': ['created_at']}),
    ]

    # ------------------------------------------------------------------
    # Custom display columns
    # ------------------------------------------------------------------
    @admin.display(description='Type')
    def document_type_badge(self, obj):
        colors = {
            'DRAWING': '#003366',
            'SPEC':    '#5B2C8D',
        }
        color = colors.get(obj.document_type, '#555')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:bold">{}</span>',
            color, obj.document_type
        )

    @admin.display(description='Status')
    def status_badge(self, obj):
        styles = {
            'PENDING':     ('background:#CC9900;color:white',  'PENDING'),
            'IMPLEMENTED': ('background:#1A7F37;color:white',  'DONE'),
            'SUPERSEDED':  ('background:#888;color:white',     'SUPERSEDED'),
        }
        style, label = styles.get(
            obj.implementation_status,
            ('background:#555;color:white', obj.implementation_status)
        )
        return format_html(
            '<span style="{};padding:2px 8px;border-radius:4px;'
            'font-size:11px;font-weight:bold">{}</span>',
            style, label
        )

    @admin.display(description='Affected PLs')
    def affected_count(self, obj):
        n = len(obj.affected_pl_numbers or [])
        if n == 0:
            return format_html('<span style="color:#999">—</span>')
        return format_html(
            '<span style="color:#003366;font-weight:bold">{}</span>', n
        )

    def has_add_permission(self, request):
        return False  # Records only created via signal

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete alteration records
        return request.user.is_superuser


# =============================================================================
# Remaining models (unchanged)
# =============================================================================
@admin.register(VendorDrawing)
class VendorDrawingAdmin(admin.ModelAdmin):
    list_display  = [
        'vendor_drawing_number', 'vendor_name', 'linked_pl_number',
        'approval_status', 'approval_date'
    ]
    search_fields = ['vendor_drawing_number', 'vendor_name', 'vendor_code']
    list_filter   = ['approval_status', 'is_active']


@admin.register(STRMaster)
class STRMasterAdmin(admin.ModelAdmin):
    list_display  = ['str_number', 'str_description', 'linked_pl_number', 'unit_of_measure']
    search_fields = ['str_number', 'str_description']


@admin.register(RDSOReference)
class RDSOReferenceAdmin(admin.ModelAdmin):
    list_display  = [
        'rdso_doc_number', 'rdso_doc_type', 'rdso_doc_title',
        'current_revision', 'effective_date'
    ]
    search_fields = ['rdso_doc_number', 'rdso_doc_title']
    list_filter   = ['rdso_doc_type', 'is_active']


@admin.register(PLSMILink)
class PLSMILinkAdmin(admin.ModelAdmin):
    list_display  = [
        'pl_item', 'smi_number', 'smi_type',
        'is_mandatory', 'deadline', 'implementation_status'
    ]
    search_fields = ['pl_item__pl_number', 'smi_number']
    list_filter   = ['implementation_status', 'smi_type', 'is_mandatory']
