from django.contrib import admin
from .models import LocomotiveType, ComponentCatalog, LookupCategory, LookupItem, MasterDataChangeLog


@admin.register(LocomotiveType)
class LocomotiveTypeAdmin(admin.ModelAdmin):
    list_display  = ['model_id', 'name', 'loco_class', 'status', 'engine_power', 'updated_at']
    list_filter   = ['status', 'engine_type']
    search_fields = ['model_id', 'name']


class LookupItemInline(admin.TabularInline):
    model = LookupItem
    extra = 1

@admin.register(LookupCategory)
class LookupCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    inlines      = [LookupItemInline]

@admin.register(ComponentCatalog)
class ComponentCatalogAdmin(admin.ModelAdmin):
    list_display  = ['part_number', 'description', 'category', 'status']
    list_filter   = ['category', 'status']
    search_fields = ['part_number', 'description']

@admin.register(MasterDataChangeLog)
class MasterDataChangeLogAdmin(admin.ModelAdmin):
    list_display  = ['action', 'model_name', 'description', 'user', 'timestamp']
    list_filter   = ['action', 'model_name']
    readonly_fields = ['timestamp']
