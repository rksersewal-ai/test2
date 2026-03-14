# =============================================================================
# FILE: apps/pdf_tools/serializers.py
# SPRINT 6
# =============================================================================
from rest_framework import serializers
from apps.pdf_tools.models import PdfJob


class PdfJobSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True
    )

    class Meta:
        model  = PdfJob
        fields = [
            'id', 'operation', 'status',
            'input_files', 'params', 'output_files',
            'error_message', 'created_by', 'created_by_name',
            'created_at', 'completed_at', 'linked_revision',
        ]
        read_only_fields = [
            'status', 'output_files', 'error_message',
            'created_by', 'created_at', 'completed_at',
        ]


class MergeRequestSerializer(serializers.Serializer):
    """POST /api/pdf/merge/"""
    file_attachment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        help_text='IDs of FileAttachment rows to merge, in order.'
    )
    output_name = serializers.CharField(default='merged.pdf')
    linked_revision_id = serializers.IntegerField(required=False, allow_null=True)


class SplitRequestSerializer(serializers.Serializer):
    """POST /api/pdf/split/"""
    file_attachment_id = serializers.IntegerField()
    page_ranges = serializers.ListField(
        child=serializers.ListField(child=serializers.IntegerField(), min_length=2, max_length=2),
        required=False, allow_null=True,
        help_text='e.g. [[1,5],[6,10]]. Mutually exclusive with pages_per_chunk.'
    )
    pages_per_chunk = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )

    def validate(self, data):
        if not data.get('page_ranges') and not data.get('pages_per_chunk'):
            raise serializers.ValidationError(
                'Provide either page_ranges or pages_per_chunk.'
            )
        return data


class RotateRequestSerializer(serializers.Serializer):
    """POST /api/pdf/rotate/"""
    file_attachment_id = serializers.IntegerField()
    angle              = serializers.ChoiceField(choices=[90, 180, 270])
    page_numbers       = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, allow_null=True,
        help_text='1-indexed page numbers. Omit to rotate all pages.'
    )


class ExtractRequestSerializer(serializers.Serializer):
    """POST /api/pdf/extract/"""
    file_attachment_id = serializers.IntegerField()
    page_numbers       = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        help_text='1-indexed pages to extract into new PDF.'
    )
    output_name = serializers.CharField(default='extracted.pdf')
