# =============================================================================
# FILE: apps/workflow/views.py
# SPRINT 4: ApprovalChainViewSet + ApprovalRequestViewSet added.
# All Sprint 1 ViewSets preserved exactly.
# =============================================================================
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.workflow.models import (
    WorkType, WorkLedgerEntry,
    ApprovalChain, ApprovalRequest, ApprovalStep,
)
from apps.workflow.serializers import (
    WorkTypeSerializer, WorkLedgerListSerializer, WorkLedgerDetailSerializer,
    ApprovalChainSerializer, ApprovalStepSerializer,
    ApprovalRequestListSerializer, ApprovalRequestDetailSerializer,
    CastVoteSerializer, InitiateApprovalSerializer,
)
from apps.workflow.filters import WorkLedgerFilter
from apps.workflow.services import WorkLedgerService, ApprovalService
from apps.core.permissions import IsEngineerOrAbove, IsAdminOrSectionHead


# ---- Sprint 1 (preserved) ---------------------------------------------------

class WorkTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = WorkType.objects.filter(is_active=True)
    serializer_class   = WorkTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkLedgerEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = WorkLedgerFilter
    search_fields      = [
        'subject', 'eoffice_subject', 'eoffice_file_number',
        'eoffice_diary_number', 'remarks',
    ]
    ordering_fields    = ['created_at', 'updated_at', 'target_date', 'received_date']
    ordering           = ['-created_at']

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


# ---- Sprint 4: Approval Engine ----------------------------------------------

class ApprovalChainViewSet(viewsets.ModelViewSet):
    """
    CRUD for ApprovalChain templates (admin / section head only).
    GET /api/workflow/approval-chains/            — list all active chains
    GET /api/workflow/approval-chains/{id}/       — detail with nested steps
    POST /api/workflow/approval-chains/           — create new chain
    """
    serializer_class   = ApprovalChainSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSectionHead]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['name']

    def get_queryset(self):
        qs = ApprovalChain.objects.prefetch_related('steps').select_related('document_type')
        if self.request.query_params.get('active_only', 'true').lower() == 'true':
            qs = qs.filter(is_active=True)
        doc_type = self.request.query_params.get('document_type')
        if doc_type:
            qs = qs.filter(document_type_id=doc_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ApprovalRequestViewSet(viewsets.GenericViewSet,
                             viewsets.mixins.ListModelMixin,
                             viewsets.mixins.RetrieveModelMixin):
    """
    Read + action endpoints for ApprovalRequests.

    POST /api/workflow/approval-requests/initiate/       — start a new run
    POST /api/workflow/approval-requests/{id}/vote/      — cast a vote
    POST /api/workflow/approval-requests/{id}/withdraw/  — withdraw request
    GET  /api/workflow/approval-requests/?status=IN_REVIEW&revision=42
    """
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields    = ['initiated_at', 'completed_at']
    ordering           = ['-initiated_at']

    def get_queryset(self):
        qs = (
            ApprovalRequest.objects
            .select_related('chain', 'revision__document', 'initiated_by')
            .prefetch_related('votes__step', 'votes__voted_by')
        )
        # Filter params
        s = self.request.query_params.get('status')
        if s:
            qs = qs.filter(status=s)
        rev = self.request.query_params.get('revision')
        if rev:
            qs = qs.filter(revision_id=rev)
        mine = self.request.query_params.get('mine')
        if mine == 'true':
            qs = qs.filter(initiated_by=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ApprovalRequestDetailSerializer
        return ApprovalRequestListSerializer

    @action(detail=False, methods=['post'], url_path='initiate')
    def initiate(self, request):
        """Start an approval run: POST {chain_id, revision_id, remarks?}"""
        ser = InitiateApprovalSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        chain    = get_object_or_404(ApprovalChain, pk=ser.validated_data['chain_id'],
                                     is_active=True)
        revision = get_object_or_404(
            __import__('apps.edms.models', fromlist=['Revision']).Revision,
            pk=ser.validated_data['revision_id']
        )
        try:
            req = ApprovalService.initiate(
                chain=chain, revision=revision,
                user=request.user,
                remarks=ser.validated_data['remarks'],
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ApprovalRequestDetailSerializer(req).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='vote')
    def vote(self, request, pk=None):
        """Cast a vote on the current step: POST {vote, comment?}"""
        req = self.get_object()
        ser = CastVoteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        step = ApprovalService.get_active_step(req)
        if not step:
            return Response({'error': 'No active step found.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            ApprovalService.cast_vote(
                request=req, step=step,
                user=request.user,
                vote=ser.validated_data['vote'],
                comment=ser.validated_data['comment'],
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        req.refresh_from_db()
        return Response(ApprovalRequestDetailSerializer(req).data)

    @action(detail=True, methods=['post'], url_path='withdraw')
    def withdraw(self, request, pk=None):
        """Withdraw an in-progress request (initiator or admin)."""
        req = self.get_object()
        if req.initiated_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only the initiator or an admin can withdraw.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            ApprovalService.withdraw(req, request.user)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        req.refresh_from_db()
        return Response(ApprovalRequestDetailSerializer(req).data)
