# =============================================================================
# FILE: apps/sanity/views.py
# SPRINT 6 — Sanity Checker API
#
# GET  /api/sanity/reports/            — list past reports
# GET  /api/sanity/reports/{id}/       — full report with issues list
# POST /api/sanity/run/                — trigger immediate check (admin)
# GET  /api/sanity/live/               — run checks synchronously, return results
#                                         (no DB save — for dashboard preview)
# =============================================================================
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response   import Response

from apps.sanity.models      import SanityReport
from apps.sanity.serializers import SanityReportSerializer, RunSanitySerializer
from apps.core.permissions   import IsAdminOrSectionHead


class SanityReportViewSet(viewsets.GenericViewSet,
                          viewsets.mixins.ListModelMixin,
                          viewsets.mixins.RetrieveModelMixin):
    serializer_class   = SanityReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSectionHead]
    queryset           = SanityReport.objects.select_related('run_by').all()

    @action(detail=False, methods=['post'], url_path='run')
    def run(self, request):
        """Queue a full sanity check via Celery."""
        ser = RunSanitySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        from apps.sanity.tasks import run_sanity_checks
        task = run_sanity_checks.delay(
            stale_draft_days = ser.validated_data['stale_draft_days'],
            user_id          = request.user.pk,
        )
        return Response(
            {'status': 'queued', 'task_id': task.id},
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=False, methods=['get'], url_path='live')
    def live(self, request):
        """
        Synchronous live check — returns issues without saving a report.
        Useful for the dashboard health widget.
        Max ~2 s on a typical LAN DB.
        """
        days = int(request.query_params.get('stale_draft_days', 90))
        from apps.sanity.checks import run_all_checks
        issues = run_all_checks(stale_draft_days=days)
        summary = {
            'total':    len(issues),
            'errors':   sum(1 for i in issues if i['severity'] == 'ERROR'),
            'warnings': sum(1 for i in issues if i['severity'] == 'WARNING'),
            'info':     sum(1 for i in issues if i['severity'] == 'INFO'),
            'issues':   issues,
        }
        return Response(summary)
