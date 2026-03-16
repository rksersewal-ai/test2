"""Audit log API — read-only, AUDIT or ADMIN role only."""
import csv
from django.http import HttpResponse
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.audit.filters import AuditLogFilter
from apps.core.permissions import IsAuditRole


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuditRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuditLogFilter
    search_fields = ['username', 'user_full_name', 'description', 'entity_identifier', 'action']
    ordering_fields = ['timestamp', 'module', 'action']
    ordering = ['-timestamp']

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """GET /api/v1/audit/logs/export/ — download filtered audit log as CSV."""
        qs = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="audit_log_{__import__("datetime").date.today()}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(['ID', 'Timestamp', 'User', 'Module', 'Action', 
                         'Entity Type', 'Entity ID', 'Entity Name', 
                         'Description', 'IP Address', 'Success'])
        for log in qs.iterator():
            writer.writerow([
                log.id,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else '',
                log.username or (log.user.username if log.user else 'System'),
                log.module, 
                log.action,
                log.entity_type, 
                log.entity_id, 
                log.entity_identifier,
                log.description,
                log.ip_address or '',
                'Yes' if log.success else 'No',
            ])
        return response
