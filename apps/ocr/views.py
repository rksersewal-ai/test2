# =============================================================================
# FILE: apps/ocr/views.py
# FIX #19b: OCRQueueViewSet now uses OCRSubmitThrottle on the queue/ endpoint
#   and OCRRetryThrottle on the retry/ action to prevent one user from
#   saturating all Celery workers by submitting hundreds of large files.
# =============================================================================
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend

from apps.ocr.models import OCRQueue
from apps.ocr.serializers import OCRQueueSerializer, OCRQueueListSerializer, OCRResultSerializer
from apps.ocr.filters import OCRQueueFilter
from apps.ocr.throttles import OCRSubmitThrottle, OCRRetryThrottle
from apps.core.permissions import IsEngineerOrAbove


class OCRQueueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for OCR queue monitoring.
    FIX #19b: Per-action throttles applied to submission and retry endpoints.
    """
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class    = OCRQueueFilter
    ordering_fields    = ['queued_at', 'priority', 'status']
    ordering           = ['priority', 'queued_at']

    def get_queryset(self):
        return OCRQueue.objects.select_related(
            'file_attachment',
            'file_attachment__revision__document',
            'result',
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OCRQueueSerializer
        return OCRQueueListSerializer

    # FIX #19b: throttle on queue submission
    def get_throttles(self):
        if self.action == 'create':
            return [OCRSubmitThrottle()]
        if self.action == 'retry':
            return [OCRRetryThrottle()]
        return super().get_throttles()

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
        """FIX #19b: OCRRetryThrottle applied via get_throttles() above."""
        item = self.get_object()
        if item.status not in (
            OCRQueue.Status.FAILED,
            OCRQueue.Status.MANUAL_REVIEW,
            OCRQueue.Status.CANCELLED,
        ):
            return Response(
                {'error': 'Only FAILED, CANCELLED or MANUAL_REVIEW items can be retried.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.status         = OCRQueue.Status.RETRY
        item.failure_reason = ''
        item.save(update_fields=['status', 'failure_reason'])
        return Response({'status': 'queued_for_retry'})

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        item = self.get_object()
        if item.status not in (
            OCRQueue.Status.PENDING,
            OCRQueue.Status.PROCESSING,
            OCRQueue.Status.RETRY,
        ):
            return Response(
                {'error': 'Only queued or processing items can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.status         = OCRQueue.Status.CANCELLED
        item.failure_reason = 'Cancelled by user.'
        item.save(update_fields=['status', 'failure_reason'])
        return Response({'status': 'cancelled'})

    @action(detail=False, methods=['get'], url_path=r'by-file/(?P<file_id>[^/.]+)/result')
    def by_file_result(self, request, file_id=None):
        queue_item = (
            self.get_queryset()
            .filter(file_attachment_id=file_id, result__isnull=False)
            .first()
        )
        if queue_item is None:
            return Response(
                {'detail': 'OCR result not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(OCRResultSerializer(queue_item.result).data)
