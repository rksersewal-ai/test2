# =============================================================================
# FILE: apps/ml_classifier/serializers.py
# SPRINT 5
# =============================================================================
from rest_framework import serializers
from apps.ml_classifier.models import ClassifierModel, ClassificationResult


class ClassifierModelSerializer(serializers.ModelSerializer):
    trained_by_name = serializers.CharField(
        source='trained_by.get_full_name', read_only=True
    )
    accuracy_pct = serializers.SerializerMethodField()

    def get_accuracy_pct(self, obj):
        return f'{obj.accuracy:.1%}' if obj.accuracy is not None else None

    class Meta:
        model  = ClassifierModel
        fields = [
            'id', 'target', 'version', 'accuracy', 'accuracy_pct',
            'training_docs', 'is_active', 'model_path', 'label_path',
            'trained_by', 'trained_by_name', 'trained_at', 'notes',
        ]
        read_only_fields = fields


class ClassificationResultSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.get_full_name', read_only=True
    )
    document_number = serializers.CharField(
        source='document.document_number', read_only=True
    )

    class Meta:
        model  = ClassificationResult
        fields = [
            'id', 'document', 'document_number', 'target',
            'predictions', 'top_label', 'top_label_id', 'top_confidence',
            'outcome', 'reviewed_by', 'reviewed_by_name', 'reviewed_at',
            'created_at',
        ]
        read_only_fields = [
            'document', 'target', 'predictions', 'top_label',
            'top_label_id', 'top_confidence', 'created_at', 'classifier',
        ]


class ClassifyRequestSerializer(serializers.Serializer):
    """Input: POST /api/ml/classify/{document_id}/"""
    # No body needed — document_id comes from URL
    pass


class AcceptPredictionSerializer(serializers.Serializer):
    """Input: POST /api/ml/results/{id}/accept/  or  /override/"""
    accepted_label_id = serializers.IntegerField(
        required=False,
        help_text='Required only for /override/. The label_id the user chose.'
    )
