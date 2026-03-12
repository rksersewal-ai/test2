from rest_framework import serializers
from apps.ocr.models import OCRQueue, OCRResult, ExtractedEntity


class OCRQueueSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(source='file.file_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = OCRQueue
        fields = [
             'id', 'file', 'file_name', 'status', 'priority', 'attempts',
            'max_attempts', 'queued_at', 'started_at', 'completed_at',
            'last_error', 'processing_time_seconds', 'ocr_engine', 'language',
            'worker_id', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['queued_at', 'started_at', 'completed_at', 'attempts', 'worker_id']


class ExtractedEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedEntity
        fields = ['id', 'entity_type', 'entity_value', 'confidence', 'context', 'page_number', 'bounding_box']


class OCRResultSerializer(serializers.ModelSerializer):
    entities = ExtractedEntitySerializer(many=True, read_only=True)
    file_name = serializers.CharField(source='file.file_name', read_only=True)

    class Meta:
        model = OCRResult
        fields = [
            'id', 'file', 'file_name', 'full_text', 'page_count', 'confidence_score',
            'page_results', 'ocr_engine', 'ocr_version', 'language_detected',
            'processing_time_seconds', 'file_size_bytes', 'processed_at', 'indexed_at', 'entities'
        ]
