from django.contrib import admin
from .models import Inspection, PunchItem


class PunchItemInline(admin.TabularInline):
    model = PunchItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at', 'closed_at', 'closed_by']
    fields = ['description', 'status', 'raised_by', 'closed_by', 'closed_at', 'remarks']


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display   = ['loco_class', 'loco_number', 'inspection_type', 'inspection_date', 'inspector', 'status', 'created_at']
    list_filter    = ['status', 'inspection_type', 'loco_class']
    search_fields  = ['loco_number', 'inspector']
    ordering       = ['-inspection_date']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines        = [PunchItemInline]


@admin.register(PunchItem)
class PunchItemAdmin(admin.ModelAdmin):
    list_display  = ['inspection', 'description', 'status', 'raised_by', 'closed_by', 'closed_at']
    list_filter   = ['status']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at', 'closed_at']
