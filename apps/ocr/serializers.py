from rest_framework import serializers
from apps.ocr.models import OCRQueue, OCRResult, OCRExtractedEntity


class OCRExtractedEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = OCRExtractedEntity
        fields = ['id', 'entity_type', 'value', 'confidence', 'page_number']


class OCRResultSerializer(serializers.ModelSerializer):
    entities = OCRExtractedEntitySerializer(many=True, read_only=True)

    class Meta:
        model = OCRResult
        fields = [
            'id', 'full_text', 'confidence', 'page_count',
            'language_detected', 'extracted_at', 'entities',
        ]


class OCRQueueSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(read_only=True)
    result = OCRResultSerializer(read_only=True)

    class Meta:
        model = OCRQueue
        fields = [
            'id', 'file_name', 'status', 'priority',
            'attempts', 'max_attempts', 'ocr_engine',
            'queued_at', 'started_at', 'completed_at',
            'processing_time_seconds', 'failure_reason',
            'result',
        ]
        read_only_fields = [
            'status', 'attempts', 'queued_at', 'started_at',
            'completed_at', 'processing_time_seconds', 'failure_reason',
        ]


class OCRQueueListSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(read_only=True)
    document_title = serializers.CharField(source='file_attachment.revision.document.title', read_only=True)
    document_id = serializers.IntegerField(source='file_attachment.revision.document_id', read_only=True)
    confidence_score = serializers.FloatField(source='result.confidence', read_only=True)
    total_pages = serializers.IntegerField(source='result.page_count', read_only=True)
    created_at = serializers.DateTimeField(source='queued_at', read_only=True)

    class Meta:
        model = OCRQueue
        fields = [
            'id', 'file_name', 'document_title', 'document_id', 'status', 'priority',
            'attempts', 'max_attempts', 'ocr_engine',
            'queued_at', 'created_at', 'completed_at', 'processing_time_seconds',
            'confidence_score', 'total_pages',
        ]
