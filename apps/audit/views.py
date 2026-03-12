from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.audit.models import AuditLog, DocumentAccessLog
from apps.audit.serializers import AuditLogSerializer, DocumentAccessLogSerializer
from apps.core.permissions import IsAuditRole


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.select_related('user').all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuditRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'module', 'success', 'username']
    search_fields = ['username', 'entity_identifier', 'description']
    ordering_fields = ['timestamp', 'module', 'action']
    ordering = ['-timestamp']


class AuditLogDetailView(generics.RetrieveAPIView):
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuditRole]


class DocumentAccessLogListView(generics.ListAPIView):
    queryset = DocumentAccessLog.objects.select_related('user').all().order_by('-timestamp')
    serializer_class = DocumentAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuditRole]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['access_type', 'document_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
