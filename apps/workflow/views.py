from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.workflow.models import WorkType, WorkLedgerEntry
from apps.workflow.serializers import WorkTypeSerializer, WorkLedgerListSerializer, WorkLedgerDetailSerializer
from apps.workflow.filters import WorkLedgerFilter
from apps.workflow.services import WorkLedgerService
from apps.core.permissions import IsEngineerOrAbove


class WorkTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkType.objects.filter(is_active=True)
    serializer_class = WorkTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkLedgerEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = WorkLedgerFilter
    search_fields = [
        'subject', 'eoffice_subject', 'eoffice_file_number',
        'eoffice_diary_number', 'remarks',
    ]
    ordering_fields = ['created_at', 'updated_at', 'target_date', 'received_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            WorkLedgerEntry.objects
            .select_related('work_type', 'section', 'assigned_to', 'created_by',
                            'linked_document', 'linked_revision')
        )

    def get_serializer_class(self):
        if self.action in ('retrieve', 'create', 'update', 'partial_update'):
            return WorkLedgerDetailSerializer
        return WorkLedgerListSerializer

    def perform_create(self, serializer):
        entry = serializer.save(created_by=self.request.user)
        WorkLedgerService.log_create(entry, self.request.user)

    def perform_update(self, serializer):
        entry = serializer.save()
        WorkLedgerService.log_update(entry, self.request.user)
