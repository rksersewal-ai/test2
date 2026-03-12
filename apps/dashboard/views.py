"""Dashboard statistics endpoints."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.edms.models import Document, Revision, FileAttachment
        from apps.workflow.models import WorkLedger
        from apps.ocr.models import OCRQueue

        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        doc_stats = Document.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(status='ACTIVE')),
            draft=Count('id', filter=Q(status='DRAFT')),
        )

        work_stats = WorkLedger.objects.aggregate(
            total=Count('id'),
            open=Count('id', filter=Q(status='OPEN')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            closed=Count('id', filter=Q(status='CLOSED')),
            closed_last_30=Count('id', filter=Q(status='CLOSED', closed_date__gte=thirty_days_ago)),
        )

        ocr_stats = OCRQueue.objects.aggregate(
            pending=Count('id', filter=Q(status='PENDING')),
            processing=Count('id', filter=Q(status='PROCESSING')),
            completed=Count('id', filter=Q(status='COMPLETED')),
            failed=Count('id', filter=Q(status='FAILED')),
            manual_review=Count('id', filter=Q(status='MANUAL_REVIEW')),
        )

        docs_by_section = (
            Document.objects
            .values('section__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        return Response({
            'documents': doc_stats,
            'work_ledger': work_stats,
            'ocr_queue': ocr_stats,
            'documents_by_section': list(docs_by_section),
            'generated_at': timezone.now().isoformat(),
        })
