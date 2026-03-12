"""OCR API views - queue management and results retrieval."""
from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.ocr.models import OCRQueue, OCRResult, ExtractedEntity
from apps.ocr.serializers import OCRQueueSerializer, OCRResultSerializer, ExtractedEntitySerializer
from apps.ocr.services import OCRService
from apps.core.permissions import IsEngineerOrAbove


class OCRQueueViewSet(viewsets.ModelViewSet):
    queryset = OCRQueue.objects.select_related('file', 'created_by').all()
    serializer_class = OCRQueueSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'ocr_engine', 'language']
    ordering_fields = ['queued_at', 'priority', 'completed_at']
    ordering = ['priority', 'queued_at']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        return instance

    @action(detail=True, methods=['post'], url_path='retry')
    def retry(self, request, pk=None):
        """Retry a failed or manual-review OCR job."""
        try:
            item = OCRService.retry_failed_item(pk)
            return Response(OCRQueueSerializer(item).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Return OCR queue status counts."""
        from django.db.models import Count, Q
        data = OCRQueue.objects.aggregate(
            pending=Count('id', filter=Q(status='PENDING')),
            processing=Count('id', filter=Q(status='PROCESSING')),
            completed=Count('id', filter=Q(status='COMPLETED')),
            failed=Count('id', filter=Q(status='FAILED')),
            retry=Count('id', filter=Q(status='RETRY')),
            manual_review=Count('id', filter=Q(status='MANUAL_REVIEW')),
        )
        return Response(data)


class OCRResultListView(generics.ListAPIView):
    queryset = OCRResult.objects.select_related('file').prefetch_related('entities').all()
    serializer_class = OCRResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ocr_engine']
    search_fields = ['full_text', 'entities__entity_value']


class OCRResultDetailView(generics.RetrieveAPIView):
    queryset = OCRResult.objects.select_related('file').prefetch_related('entities').all()
    serializer_class = OCRResultSerializer
    permission_classes = [permissions.IsAuthenticated]
