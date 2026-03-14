from rest_framework import serializers
from .models import OCRJob


class OCRJobSerializer(serializers.ModelSerializer):
    queued_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = OCRJob
        fields = [
            'id', 'document_id', 'document_title', 'file_name', 'engine',
            'status', 'page_count', 'error_message',
            'queued_by', 'queued_by_name',
            'started_at', 'completed_at', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'queued_by_name', 'started_at', 'completed_at',
            'created_at', 'updated_at', 'error_message',
        ]

    def get_queued_by_name(self, obj):
        if obj.queued_by:
            return obj.queued_by.get_full_name() or obj.queued_by.username
        return None
