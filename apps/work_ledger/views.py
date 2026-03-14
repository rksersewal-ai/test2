# =============================================================================
# FILE: apps/work_ledger/views.py
# =============================================================================
from django.contrib.auth    import get_user_model
from django.db.models       import Count, Sum, Q
from django.utils           import timezone
from rest_framework         import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response   import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models       import WorkCategory, WorkEntry, WorkVerification, WorkTarget, WorkStatus
from .serializers  import (
    WorkCategorySerializer,
    WorkEntryReadSerializer, WorkEntryWriteSerializer,
    WorkEntrySubmitSerializer, WorkEntryVerifySerializer,
    WorkTargetSerializer,
)
from .permissions  import IsOwnerOrSupervisor, IsSupervisorOrAbove
from .filters      import WorkEntryFilter

User = get_user_model()


# ---------------------------------------------------------------------------
# WorkCategoryViewSet
# ---------------------------------------------------------------------------
class WorkCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = WorkCategory.objects.filter(is_active=True).order_by('sort_order', 'name')
    serializer_class = WorkCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['name', 'code', 'work_type']


# ---------------------------------------------------------------------------
# WorkEntryViewSet
# ---------------------------------------------------------------------------
class WorkEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrSupervisor]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = WorkEntryFilter
    search_fields      = ['description', 'reference_number', 'remarks', 'linked_drawing_number']
    ordering_fields    = ['work_date', 'created_at', 'status', 'work_type']
    ordering           = ['-work_date', '-created_at']

    def get_queryset(self):
        user = self.request.user
        role = getattr(getattr(user, 'role', None), 'role_name', '').upper()
        qs   = WorkEntry.objects.select_related(
            'user', 'category', 'submitted_to'
        ).prefetch_related('verifications', 'attachments')

        # Admins/Officers/WM see all; others see only their own
        if user.is_staff or role in ('ADMIN', 'OFFICER', 'WM'):
            return qs
        if role == 'SSE':
            # SSE sees own + entries submitted to them
            return qs.filter(Q(user=user) | Q(submitted_to=user))
        return qs.filter(user=user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return WorkEntryWriteSerializer
        return WorkEntryReadSerializer

    # --- Custom actions ----------------------------------------------------

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """Submit a DRAFT/RETURNED entry for supervisor verification."""
        entry = self.get_object()
        serializer = WorkEntrySubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        supervisor_id = serializer.validated_data['supervisor_id']
        try:
            supervisor = User.objects.get(pk=supervisor_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Supervisor not found.'}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            entry.submit(supervisor)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            WorkEntryReadSerializer(entry, context={'request': request}).data
        )

    @action(detail=True, methods=['post'], url_path='verify',
            permission_classes=[IsAuthenticated, IsSupervisorOrAbove])
    def verify(self, request, pk=None):
        """Verify, approve or return a submitted entry."""
        entry      = self.get_object()
        serializer = WorkEntryVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_val = serializer.validated_data['action']
        remarks    = serializer.validated_data.get('remarks', '')

        if not entry.can_verify():
            return Response(
                {'error': 'Entry is not pending verification.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = {
            'VERIFIED': WorkStatus.VERIFIED,
            'APPROVED': WorkStatus.APPROVED,
            'RETURNED': WorkStatus.RETURNED,
        }[action_val]

        entry.status = new_status
        entry.save(update_fields=['status'])

        WorkVerification.objects.create(
            work_entry=entry,
            verifier=request.user,
            action=action_val,
            remarks=remarks,
        )

        return Response(
            WorkEntryReadSerializer(entry, context={'request': request}).data
        )

    @action(detail=False, methods=['get'], url_path='my-entries')
    def my_entries(self, request):
        """Return only the authenticated user's entries with summary counts."""
        qs = WorkEntry.objects.filter(user=request.user).select_related('category')

        # Optional date filter
        date_from = request.query_params.get('from')
        date_to   = request.query_params.get('to')
        if date_from:
            qs = qs.filter(work_date__gte=date_from)
        if date_to:
            qs = qs.filter(work_date__lte=date_to)

        summary = qs.values('status').annotate(count=Count('id')).order_by('status')
        page    = self.paginate_queryset(qs.order_by('-work_date'))
        data    = WorkEntryReadSerializer(page, many=True, context={'request': request}).data

        return self.get_paginated_response({
            'summary': list(summary),
            'entries': data,
        })

    @action(detail=False, methods=['get'], url_path='team-summary',
            permission_classes=[IsAuthenticated, IsSupervisorOrAbove])
    def team_summary(self, request):
        """Return aggregated work stats per team member for a date range."""
        date_from = request.query_params.get('from', str(timezone.now().date().replace(day=1)))
        date_to   = request.query_params.get('to',   str(timezone.now().date()))

        qs = WorkEntry.objects.filter(
            work_date__gte=date_from,
            work_date__lte=date_to,
        ).values(
            'user__id', 'user__first_name', 'user__last_name'
        ).annotate(
            total_entries  = Count('id'),
            draft_count    = Count('id', filter=Q(status='DRAFT')),
            submitted_count= Count('id', filter=Q(status='SUBMITTED')),
            verified_count = Count('id', filter=Q(status='VERIFIED')),
            approved_count = Count('id', filter=Q(status='APPROVED')),
            total_effort   = Sum('effort_value'),
        ).order_by('user__last_name')

        return Response({
            'period': {'from': date_from, 'to': date_to},
            'team_summary': list(qs),
        })


# ---------------------------------------------------------------------------
# WorkTargetViewSet
# ---------------------------------------------------------------------------
class WorkTargetViewSet(viewsets.ModelViewSet):
    serializer_class   = WorkTargetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['user', 'period_type', 'work_type', 'is_active']
    ordering           = ['-period_start']

    def get_queryset(self):
        user = self.request.user
        role = getattr(getattr(user, 'role', None), 'role_name', '').upper()
        if user.is_staff or role in ('ADMIN', 'OFFICER', 'WM', 'SSE'):
            return WorkTarget.objects.select_related('user', 'set_by').all()
        return WorkTarget.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(set_by=self.request.user)
