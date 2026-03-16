from django.contrib import admin
from .models import RetentionPolicy, DocumentLifecycle, LifecycleEvent


@admin.register(RetentionPolicy)
class RetentionPolicyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'retention_years', 'action_after_retention', 'legal_basis', 'is_active']
    list_filter   = ['action_after_retention', 'is_active']
    search_fields = ['name', 'legal_basis']


@admin.register(DocumentLifecycle)
class DocumentLifecycleAdmin(admin.ModelAdmin):
    list_display  = ['document', 'state', 'policy', 'retention_due_date', 'archived_at']
    list_filter   = ['state']
    search_fields = ['document__document_number']
    raw_id_fields = ['document']


@admin.register(LifecycleEvent)
class LifecycleEventAdmin(admin.ModelAdmin):
    list_display  = ['document', 'from_state', 'to_state', 'triggered_by', 'triggered_at']
    readonly_fields = ['triggered_at']
    search_fields = ['document__document_number']
