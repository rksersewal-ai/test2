# =============================================================================
# FILE: backend/master/admin.py
# Django admin registrations for all master app models including PL Master
# =============================================================================
from django.contrib import admin
from .models import LocomotiveType, ComponentCatalog, LookupCategory, LookupItem, MasterDataChangeLog
from .models_pl_master import PLMasterItem
from .models_pl_docs import PLVendorInfo, PLLinkedDocument
from .models_tech_eval import PLTechEvalDocument


@admin.register(LocomotiveType)
class LocomotiveTypeAdmin(admin.ModelAdmin):
    list_display  = ['model_id', 'name', 'loco_class', 'status', 'manufacturer']
    search_fields = ['model_id', 'name']
    list_filter   = ['status']


@admin.register(ComponentCatalog)
class ComponentCatalogAdmin(admin.ModelAdmin):
    list_display  = ['part_number', 'description', 'category', 'status', 'supplier']
    search_fields = ['part_number', 'description']
    list_filter   = ['category', 'status']


@admin.register(LookupCategory)
class LookupCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(MasterDataChangeLog)
class MasterDataChangeLogAdmin(admin.ModelAdmin):
    list_display  = ['action', 'model_name', 'object_id', 'user', 'timestamp']
    list_filter   = ['action', 'model_name']
    readonly_fields = ['timestamp']


@admin.register(PLMasterItem)
class PLMasterItemAdmin(admin.ModelAdmin):
    list_display   = ['pl_number', 'description', 'uvam_id', 'inspection_category', 'safety_item', 'is_active']
    list_filter    = ['inspection_category', 'safety_item', 'is_active']
    search_fields  = ['pl_number', 'description', 'uvam_id']
    readonly_fields= ['created_at', 'updated_at', 'created_by', 'updated_by']


@admin.register(PLVendorInfo)
class PLVendorInfoAdmin(admin.ModelAdmin):
    list_display  = ['pl_number', 'vendor_type', 'uvam_vd_number', 'updated_at']
    list_filter   = ['vendor_type']
    search_fields = ['pl_number', 'uvam_vd_number']


@admin.register(PLLinkedDocument)
class PLLinkedDocumentAdmin(admin.ModelAdmin):
    list_display  = ['pl_number', 'document_number', 'category', 'linked_by', 'linked_at']
    list_filter   = ['category']
    search_fields = ['pl_number', 'document_number', 'document_title']


@admin.register(PLTechEvalDocument)
class PLTechEvalDocumentAdmin(admin.ModelAdmin):
    list_display  = ['pl_number', 'tender_number', 'eval_year', 'file_name', 'file_format', 'uploaded_at']
    list_filter   = ['file_format']
    search_fields = ['pl_number', 'tender_number']
    readonly_fields=['file_name', 'file_format', 'file_size_kb', 'uploaded_at']
