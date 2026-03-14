from django.contrib import admin
from .models import LocoConfig, ECN


@admin.register(LocoConfig)
class LocoConfigAdmin(admin.ModelAdmin):
    list_display  = ['loco_class', 'serial_no', 'config_version', 'ecn_ref', 'effective_date', 'changed_by', 'status', 'created_at']
    list_filter   = ['loco_class', 'status']
    search_fields = ['serial_no', 'ecn_ref', 'config_version']
    ordering      = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'created_by']


@admin.register(ECN)
class ECNAdmin(admin.ModelAdmin):
    list_display  = ['ecn_number', 'subject', 'loco_class', 'raised_by', 'date', 'status', 'approved_by', 'approved_at']
    list_filter   = ['loco_class', 'status']
    search_fields = ['ecn_number', 'subject']
    ordering      = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    filter_horizontal = ['affected_configs']
