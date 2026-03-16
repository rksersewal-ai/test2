# =============================================================================
# FILE: apps/dashboard/views.py
# SPRINT 2 additions:
#   - UserSavedViewViewSet    CRUD + pin/unpin + reorder  (Feature #7)
# DashboardStatsView preserved exactly from Phase 1.
# =============================================================================
from django.utils import timezone
from django.db import transaction
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.edms.models import Document
from apps.workflow.models import WorkLedgerEntry
from apps.ocr.models import OCRQueue
from apps.dashboard.models import UserSavedView
from apps.dashboard.serializers import UserSavedViewSerializer, ReorderSavedViewsSerializer


# ---------------------------------------------------------------------------
# Existing — preserved exactly
# ---------------------------------------------------------------------------

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doc_qs = Document.objects.values('status').annotate(count=Count('id'))
        doc_counts = {row['status']: row['count'] for row in doc_qs}

        wl_qs = WorkLedgerEntry.objects.values('status').annotate(count=Count('id'))
        wl_counts = {row['status']: row['count'] for row in wl_qs}

        ocr_qs = OCRQueue.objects.values('status').annotate(count=Count('id'))
        ocr_counts = {row['status']: row['count'] for row in ocr_qs}

        from apps.edms.repository import DocumentRepository
        by_section = list(DocumentRepository.documents_by_section()[:15])

        return Response({
            'generated_at': timezone.now().isoformat(),
            'documents': {
                'total':      sum(doc_counts.values()),
                'active':     doc_counts.get('ACTIVE', 0),
                'draft':      doc_counts.get('DRAFT', 0),
                'obsolete':   doc_counts.get('OBSOLETE', 0),
                'superseded': doc_counts.get('SUPERSEDED', 0),
            },
            'work_ledger': {
                'open':        wl_counts.get('OPEN', 0),
                'in_progress': wl_counts.get('IN_PROGRESS', 0),
                'on_hold':     wl_counts.get('ON_HOLD', 0),
                'closed':      wl_counts.get('CLOSED', 0),
            },
            'ocr_queue': {
                'pending':       ocr_counts.get('PENDING', 0),
                'processing':    ocr_counts.get('PROCESSING', 0),
                'completed':     ocr_counts.get('COMPLETED', 0),
                'failed':        ocr_counts.get('FAILED', 0),
                'manual_review': ocr_counts.get('MANUAL_REVIEW', 0),
            },
            'documents_by_section': by_section,
        })


# ---------------------------------------------------------------------------
# Sprint 2 — Feature #7: Saved Views ViewSet
# ---------------------------------------------------------------------------

class UserSavedViewViewSet(viewsets.ModelViewSet):
    """
    CRUD for the current user's saved views.
    All queries are scoped to request.user — users cannot see each other's views.

    Extra actions:
      POST .../pin/       — toggle is_pinned
      POST .../reorder/   — bulk update sort_order
    """
    serializer_class   = UserSavedViewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields    = ['sort_order', 'module', 'view_name']
    ordering           = ['module', 'sort_order']

    def get_queryset(self):
        qs     = UserSavedView.objects.filter(user=self.request.user)
        module = self.request.query_params.get('module')
        if module:
            qs = qs.filter(module=module)
        pinned = self.request.query_params.get('pinned')
        if pinned == 'true':
            qs = qs.filter(is_pinned=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='pin')
    def pin(self, request, pk=None):
        """Toggle is_pinned for this saved view."""
        view           = self.get_object()
        view.is_pinned = not view.is_pinned
        view.save(update_fields=['is_pinned', 'updated_at'])
        return Response({
            'id':        view.pk,
            'is_pinned': view.is_pinned,
        })

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        """
        Bulk-update sort_order for multiple saved views.
        Body: {"items": [{"id": 3, "sort_order": 0}, {"id": 7, "sort_order": 1}]}
        """
        serializer = ReorderSavedViewsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            for item in serializer.validated_data['items']:
                UserSavedView.objects.filter(
                    pk=item['id'], user=request.user  # user-scoped safety
                ).update(sort_order=item['sort_order'])

        return Response({'reordered': len(serializer.validated_data['items'])})
