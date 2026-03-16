from django.contrib import admin
from .models import BOMTree, BOMNode, BOMSnapshot

@admin.register(BOMTree)
class BOMTreeAdmin(admin.ModelAdmin):
    list_display = ['loco_type', 'variant', 'is_active', 'created_at']
    list_filter  = ['loco_type', 'is_active']
    search_fields= ['loco_type', 'variant']

@admin.register(BOMNode)
class BOMNodeAdmin(admin.ModelAdmin):
    list_display   = ['pl_number', 'description', 'tree', 'node_type', 'inspection_category', 'level', 'quantity']
    list_filter    = ['node_type', 'inspection_category', 'safety_item', 'is_active']
    search_fields  = ['pl_number', 'description']
    readonly_fields= ['level', 'created_at', 'updated_at']
    raw_id_fields  = ['parent', 'tree']

@admin.register(BOMSnapshot)
class BOMSnapshotAdmin(admin.ModelAdmin):
    list_display   = ['name', 'tree', 'created_by', 'created_at']
    search_fields  = ['name']
    readonly_fields= ['created_at']
