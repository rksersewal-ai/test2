# =============================================================================
# FILE: backend/ocr_queue/views.py
# =============================================================================
from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import OCRJob
from .serializers import OCRJobSerializer


class OCRJobViewSet(viewsets.ModelViewSet):
    queryset = OCRJob.objects.select_related('queued_by').all()
    serializer_class = OCRJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'engine']
    search_fields    = ['document_title', 'file_name']
    ordering_fields  = ['created_at', 'status']

    @action(detail=True, methods=['post'], url_path='retry')
    def retry(self, request, pk=None):
        """POST /api/ocr/queue/:id/retry/ — re-queue a FAILED job."""
        job = self.get_object()
        if job.status != 'FAILED':
            return Response({'detail': 'Only FAILED jobs can be retried.'}, status=400)
        job.status        = 'PENDING'
        job.error_message = ''
        job.started_at    = None
        job.completed_at  = None
        job.save(update_fields=['status', 'error_message', 'started_at', 'completed_at'])
        return Response(OCRJobSerializer(job).data)

    @action(detail=True, methods=['get'], url_path='text')
    def text(self, request, pk=None):
        """GET /api/ocr/queue/:id/text/ — return extracted text for a COMPLETED job."""
        job = self.get_object()
        if job.status != 'COMPLETED':
            return Response({'detail': 'Text only available for COMPLETED jobs.'}, status=400)
        return Response({
            'id':             job.id,
            'document_title': job.document_title,
            'text':           job.extracted_text,
            'page_count':     job.page_count,
        })
