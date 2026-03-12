"""Dashboard statistics endpoint.

GET /api/v1/dashboard/stats/
Returns a single JSON object with live counts suitable for the
React DashboardPage stat cards (no caching — LAN query is fast enough).
"""
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.edms.models import Document
from apps.workflow.models import WorkLedgerEntry
from apps.ocr.models import OCRQueue


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Documents
        doc_qs = Document.objects.values('status')
        doc_counts = {}
        for row in doc_qs.iterator():
            doc_counts[row['status']] = doc_counts.get(row['status'], 0) + 1

        # Work ledger
        wl_qs = WorkLedgerEntry.objects.values('status')
        wl_counts = {}
        for row in wl_qs.iterator():
            wl_counts[row['status']] = wl_counts.get(row['status'], 0) + 1

        # OCR
        ocr_qs = OCRQueue.objects.values('status')
        ocr_counts = {}
        for row in ocr_qs.iterator():
            ocr_counts[row['status']] = ocr_counts.get(row['status'], 0) + 1

        # Documents by section (top 15)
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
