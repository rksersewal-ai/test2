# =============================================================================
# FILE: backend/audit_log/views.py
# =============================================================================
import csv
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['action', 'model']
    search_fields      = ['user__username', 'user__first_name', 'user__last_name',
                          'object_repr', 'description']
    ordering_fields    = ['timestamp', 'action', 'model']

    def get_queryset(self):
        qs = AuditLog.objects.select_related('user').all()
        date_from = self.request.query_params.get('date_from')
        date_to   = self.request.query_params.get('date_to')
        if date_from:
            d = parse_date(date_from)
            if d: qs = qs.filter(timestamp__date__gte=d)
        if date_to:
            d = parse_date(date_to)
            if d: qs = qs.filter(timestamp__date__lte=d)
        return qs

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """GET /api/audit/logs/export/ — download filtered audit log as CSV."""
        qs = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="audit_log_{__import__("datetime").date.today()}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(['ID', 'Timestamp', 'User', 'Action', 'Model',
                         'Object ID', 'Object', 'IP Address', 'Description'])
        for log in qs.iterator():
            writer.writerow([
                log.id,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else '',
                log.user.username if log.user else 'System',
                log.action, log.model, log.object_id, log.object_repr,
                log.ip_address or '', log.description,
            ])
        return response
