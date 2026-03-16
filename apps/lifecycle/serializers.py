from rest_framework import serializers
from .models import RetentionPolicy, DocumentLifecycle, LifecycleEvent


class RetentionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model  = RetentionPolicy
        fields = ['id', 'name', 'description', 'retention_years',
                  'action_after_retention', 'legal_basis', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class DocumentLifecycleSerializer(serializers.ModelSerializer):
    document_number = serializers.CharField(source='document.document_number', read_only=True)
    policy_name     = serializers.CharField(source='policy.name', read_only=True, default=None)

    class Meta:
        model  = DocumentLifecycle
        fields = [
            'id', 'document', 'document_number', 'policy', 'policy_name',
            'state', 'created_date', 'retention_due_date', 'legal_hold_reason',
            'legal_hold_at', 'archived_at', 'deleted_at', 'notes', 'updated_at',
        ]
        read_only_fields = ['id', 'document_number', 'policy_name', 'updated_at']


class LifecycleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LifecycleEvent
        fields = ['id', 'document', 'from_state', 'to_state',
                  'triggered_by', 'triggered_at', 'reason']
        read_only_fields = ['id', 'triggered_at']
