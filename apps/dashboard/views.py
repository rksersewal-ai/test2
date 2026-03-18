# =============================================================================
# FILE: apps/dashboard/views.py
# SPRINT 2 additions:
#   - UserSavedViewViewSet    CRUD + pin/unpin + reorder  (Feature #7)
# DashboardStatsView preserved exactly from Phase 1.
# =============================================================================
from django.utils import timezone
from django.db import transaction
from django.db.models import Count
from django.db.utils import OperationalError, ProgrammingError
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.edms.models import Document
from apps.workflow.models import WorkLedgerEntry, ApprovalRequest
from apps.ocr.models import OCRQueue
from apps.dashboard.models import UserSavedView
from apps.dashboard.serializers import UserSavedViewSerializer, ReorderSavedViewsSerializer


# ---------------------------------------------------------------------------
# Existing — preserved exactly
# ---------------------------------------------------------------------------

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_model = get_user_model()

        # Documents
        doc_counts = {
            item['status']: item['count']
            for item in Document.objects.values('status').annotate(count=Count('status'))
        }

        # Work ledger
        wl_counts = {
            item['status']: item['count']
            for item in WorkLedgerEntry.objects.values('status').annotate(count=Count('status'))
        }

        # OCR
        ocr_counts = {
            item['status']: item['count']
            for item in OCRQueue.objects.values('status').annotate(count=Count('status'))
        }

        # Documents by section (top 15)
        from apps.edms.repository import DocumentRepository
        by_section = list(DocumentRepository.documents_by_section()[:15])

        # Dashboard home widgets
        recent_docs = list(
            Document.objects.select_related('created_by')
            .order_by('-updated_at')[:8]
        )
        try:
            pending_qs = (
                ApprovalRequest.objects.select_related('revision__document', 'initiated_by')
                .filter(status__in=[
                    ApprovalRequest.Status.PENDING,
                    ApprovalRequest.Status.IN_REVIEW,
                ])
                .order_by('-initiated_at')
            )
            pending_count = pending_qs.count()
            pending_items = list(pending_qs[:8])
        except (OperationalError, ProgrammingError):
            pending_count = 0
            pending_items = []
        total_documents = sum(doc_counts.values())
        actionable_ocr = (
            ocr_counts.get('PENDING', 0)
            + ocr_counts.get('PROCESSING', 0)
            + ocr_counts.get('MANUAL_REVIEW', 0)
        )

        return Response({
            'generated_at': timezone.now().isoformat(),
            'stats': {
                'total_documents': total_documents,
                'pending_approvals': pending_count,
                'ocr_queue': actionable_ocr,
                'total_users': user_model.objects.filter(is_active=True).count(),
            },
            'documents': {
                'total':      total_documents,
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
            'recent_docs': [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'doc_number': doc.document_number,
                    'status': doc.status,
                    'updated_at': doc.updated_at,
                }
                for doc in recent_docs
            ],
            'pending_approvals': [
                {
                    'id': item.revision.document_id,
                    'title': item.revision.document.title,
                    'doc_number': item.revision.document.document_number,
                    'created_by_name': (
                        item.initiated_by.full_name
                        if item.initiated_by and item.initiated_by.full_name
                        else (item.initiated_by.username if item.initiated_by else '')
                    ),
                    'created_at': item.initiated_at,
                }
                for item in pending_items
            ],
        })


class DashboardTrendView(APIView):
    """
    Returns time-series data for documents and work ledger entries for charts.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import TruncMonth
        from django.db.models import Count
        import datetime

        # Get the last 6 months
        today = datetime.date.today()
        six_months_ago = today.replace(day=1) - datetime.timedelta(days=150)

        # Documents trend
        docs_trend = list(Document.objects.filter(created_at__gte=six_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month'))

        # Work Ledger trend
        wl_trend = list(WorkLedgerEntry.objects.filter(created_at__gte=six_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month'))

        # Format output
        for d in docs_trend:
            if d['month']:
                d['month'] = d['month'].strftime('%Y-%m')
        
        for w in wl_trend:
            if w['month']:
                w['month'] = w['month'].strftime('%Y-%m')

        return Response({
            'documents': docs_trend,
            'work_ledger': wl_trend
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
