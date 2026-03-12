from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from apps.ocr.models import OCRQueue
from apps.ocr.serializers import OCRQueueSerializer, OCRQueueListSerializer
from apps.ocr.filters import OCRQueueFilter
from apps.core.permissions import IsEngineerOrAbove


class OCRQueueViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OCRQueueFilter
    ordering_fields = ['queued_at', 'priority', 'status']
    ordering = ['priority', 'queued_at']

    def get_queryset(self):
        return OCRQueue.objects.select_related('file_attachment', 'result')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OCRQueueSerializer
        return OCRQueueListSerializer

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        agg = (
            OCRQueue.objects
            .values('status')
            .annotate(count=Count('id'))
        )
        result = {row['status'].lower(): row['count'] for row in agg}
        return Response(result)

    @action(detail=True, methods=['post'], url_path='retry')
    def retry(self, request, pk=None):
        item = self.get_object()
        if item.status not in (OCRQueue.Status.FAILED, OCRQueue.Status.MANUAL_REVIEW):
            return Response(
                {'error': 'Only FAILED or MANUAL_REVIEW items can be retried.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.status = OCRQueue.Status.RETRY
        item.failure_reason = ''
        item.save(update_fields=['status', 'failure_reason'])
        return Response({'status': 'queued_for_retry'})
