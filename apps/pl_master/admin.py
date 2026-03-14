# =============================================================================
# FILE: apps/pl_master/admin.py
# =============================================================================
from django.contrib import admin
from .models import (
    ControllingAgency, PLMaster, DrawingMaster, SpecificationMaster,
    VendorDrawing, STRMaster, RDSOReference, AlterationHistory,
    PLDrawingLink, PLSpecLink, PLStandardLink, PLSMILink,
    PLAlternate, PLLocoApplicability,
)


@admin.register(ControllingAgency)
class ControllingAgencyAdmin(admin.ModelAdmin):
    list_display  = ['agency_code', 'agency_name', 'agency_type', 'is_active']
    search_fields = ['agency_code', 'agency_name']
    list_filter   = ['is_active']


class PLDrawingLinkInline(admin.TabularInline):
    model  = PLDrawingLink
    extra  = 0
    fields = ['drawing', 'is_primary', 'link_purpose', 'is_active']


class PLSpecLinkInline(admin.TabularInline):
    model  = PLSpecLink
    extra  = 0
    fields = ['specification', 'is_primary', 'link_purpose', 'is_active']


class PLSMILinkInline(admin.TabularInline):
    model  = PLSMILink
    extra  = 0
    fields = ['smi_number', 'smi_type', 'is_mandatory', 'deadline', 'implementation_status']


class PLAlternateInline(admin.TabularInline):
    model  = PLAlternate
    extra  = 0
    fk_name = 'pl_item'
    fields = ['alternate_pl', 'interchangeable', 'remarks']


class PLLocoApplicabilityInline(admin.TabularInline):
    model  = PLLocoApplicability
    extra  = 0
    fields = ['loco_type', 'assembly_group', 'qty_per_loco', 'remarks']


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


@admin.register(DrawingMaster)
class DrawingMasterAdmin(admin.ModelAdmin):
    list_display  = [
        'drawing_number', 'drawing_title', 'drawing_type',
        'current_alteration', 'controlling_agency', 'drawing_readable', 'is_active'
    ]
    search_fields = ['drawing_number', 'drawing_title']
    list_filter   = ['drawing_type', 'controlling_agency', 'drawing_readable', 'is_latest', 'is_active']


@admin.register(SpecificationMaster)
class SpecificationMasterAdmin(admin.ModelAdmin):
    list_display  = [
        'spec_number', 'spec_title', 'spec_type',
        'current_alteration', 'controlling_agency', 'is_active'
    ]
    search_fields = ['spec_number', 'spec_title']
    list_filter   = ['spec_type', 'controlling_agency', 'is_latest', 'is_active']


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


@admin.register(AlterationHistory)
class AlterationHistoryAdmin(admin.ModelAdmin):
    list_display  = [
        'document_type', 'document_number', 'alteration_number',
        'alteration_date', 'implementation_status', 'source_agency'
    ]
    search_fields = ['document_number', 'alteration_number', 'source_reference']
    list_filter   = ['document_type', 'implementation_status', 'source_agency']
    readonly_fields = ['created_at']


@admin.register(PLSMILink)
class PLSMILinkAdmin(admin.ModelAdmin):
    list_display  = [
        'pl_item', 'smi_number', 'smi_type',
        'is_mandatory', 'deadline', 'implementation_status'
    ]
    search_fields = ['pl_item__pl_number', 'smi_number']
    list_filter   = ['implementation_status', 'smi_type', 'is_mandatory']
