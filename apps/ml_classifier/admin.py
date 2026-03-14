# =============================================================================
# FILE: apps/ml_classifier/admin.py
# SPRINT 5 — Django Admin for ClassifierModel + ClassificationResult
# =============================================================================
from django.contrib import admin
from apps.ml_classifier.models import ClassifierModel, ClassificationResult


@admin.register(ClassifierModel)
class ClassifierModelAdmin(admin.ModelAdmin):
    list_display   = ['target', 'version', 'accuracy', 'training_docs', 'is_active', 'trained_at']
    list_filter    = ['target', 'is_active']
    ordering       = ['target', '-version']
    readonly_fields = [
        'target', 'version', 'model_path', 'label_path',
        'accuracy', 'training_docs', 'trained_by', 'trained_at',
    ]

    def has_add_permission(self, request):
        return False  # models are created by pipeline only


@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):
    list_display  = ['document', 'target', 'top_label', 'top_confidence', 'outcome', 'created_at']
    list_filter   = ['target', 'outcome']
    search_fields = ['document__document_number', 'top_label']
    readonly_fields = [
        'document', 'classifier', 'target', 'predictions',
        'top_label', 'top_label_id', 'top_confidence', 'created_at',
    ]
