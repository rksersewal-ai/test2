# =============================================================================
# FILE: apps/sdr/serializers.py
# =============================================================================
from rest_framework import serializers
from django.utils   import timezone

from .models import SDRRequest, SDRResponse, SDRAttachment


class SDRAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model  = SDRAttachment
        fields = [
            'id', 'attached_to_type', 'sdr_request', 'sdr_response',
            'uploaded_by', 'uploaded_by_name',
            'file', 'file_name', 'file_size', 'description', 'uploaded_at',
        ]
        read_only_fields = ['uploaded_at', 'uploaded_by']


class SDRResponseSerializer(serializers.ModelSerializer):
    responded_by_name = serializers.CharField(source='responded_by.get_full_name', read_only=True)
    attachments       = SDRAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model  = SDRResponse
        fields = [
            'id', 'sdr_request', 'response_type',
            'responded_by', 'responded_by_name',
            'technical_response', 'clarified_drawing', 'clarified_alteration',
            'dimension_reference', 'action_required',
            'linked_smi', 'deviation_permitted', 'concession_reference',
            'eoffice_file_no',
            'attachments', 'responded_at', 'updated_at',
        ]
        read_only_fields = ['responded_at', 'updated_at', 'responded_by']


class SDRRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    raised_by_name  = serializers.CharField(source='raised_by.get_full_name', read_only=True)
    assigned_to_name= serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    response_count  = serializers.SerializerMethodField()

    class Meta:
        model  = SDRRequest
        fields = [
            'id', 'sdr_number', 'subject', 'clarification_type',
            'drawing_number', 'pl_number', 'loco_type', 'loco_number',
            'urgency', 'status', 'production_hold',
            'raised_by', 'raised_by_name',
            'assigned_to', 'assigned_to_name',
            'required_by_date', 'target_response_date',
            'response_count', 'created_at',
        ]

    def get_response_count(self, obj):
        return obj.responses.count()


class SDRRequestDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail / create view."""
    raised_by_name   = serializers.CharField(source='raised_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    closed_by_name   = serializers.CharField(source='closed_by.get_full_name', read_only=True)
    responses        = SDRResponseSerializer(many=True, read_only=True)
    attachments      = SDRAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model  = SDRRequest
        fields = '__all__'
        read_only_fields = [
            'sdr_number', 'raised_by', 'status',
            'assigned_by', 'assigned_at',
            'closed_by', 'closed_at',
            'created_at', 'updated_at',
        ]
