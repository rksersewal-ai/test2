"""Audit log API — read-only, AUDIT or ADMIN role only."""
from rest_framework import viewsets, permissions, filters
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
