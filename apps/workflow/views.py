"""Workflow / LDO Work Ledger views."""
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.workflow.models import WorkLedger, WorkType, Vendor, Tender
from apps.workflow.serializers import WorkLedgerSerializer, WorkTypeSerializer, VendorSerializer, TenderSerializer
from apps.core.permissions import IsEngineerOrAbove


class WorkTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkType.objects.filter(is_active=True).all()
    serializer_class = WorkTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.filter(is_active=True).all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']


class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.select_related('created_by').all()
    serializer_class = TenderSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['tender_number', 'title', 'eoffice_file_number']
    ordering_fields = ['created_at', 'closing_date']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WorkLedgerViewSet(viewsets.ModelViewSet):
    queryset = WorkLedger.objects.select_related(
        'work_type', 'section', 'assigned_to', 'document', 'revision', 'tender', 'vendor', 'created_by'
    ).all()
    serializer_class = WorkLedgerSerializer
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'section', 'work_type', 'assigned_to']
    search_fields = ['subject', 'eoffice_file_number', 'eoffice_subject', 'remarks']
    ordering_fields = ['created_at', 'received_date', 'closed_date']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
