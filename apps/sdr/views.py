# =============================================================================
# FILE: apps/sdr/views.py
# =============================================================================
from django.utils  import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response   import Response
from rest_framework.permissions import IsAuthenticated

from .models       import SDRRequest, SDRResponse, SDRAttachment
from .serializers  import (
    SDRRequestListSerializer, SDRRequestDetailSerializer,
    SDRResponseSerializer, SDRAttachmentSerializer,
)


class SDRRequestViewSet(viewsets.ModelViewSet):
    """
    CRUD + workflow actions for Shop Drawing Requests.

    Actions:
        POST   /sdr/requests/                   create (DRAFT)
        POST   /sdr/requests/{id}/submit/       DRAFT → SUBMITTED
        POST   /sdr/requests/{id}/assign/       SUBMITTED → ASSIGNED
        POST   /sdr/requests/{id}/start/        ASSIGNED → IN_PROGRESS
        POST   /sdr/requests/{id}/respond/      IN_PROGRESS → RESPONDED
        POST   /sdr/requests/{id}/close/        RESPONDED → CLOSED
        POST   /sdr/requests/{id}/escalate/     any open → ESCALATED
        POST   /sdr/requests/{id}/reject/       SUBMITTED/ASSIGNED → REJECTED
        GET    /sdr/requests/my-requests/       own SDRs
        GET    /sdr/requests/pending-action/    assigned to me, open
        GET    /sdr/requests/overdue/           past target_response_date
    """
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = [
        'status', 'urgency', 'clarification_type',
        'raising_section', 'loco_type', 'production_hold',
        'assigned_to', 'raised_by',
    ]
    search_fields      = ['sdr_number', 'subject', 'drawing_number', 'pl_number', 'query_description']
    ordering_fields    = ['created_at', 'urgency', 'status', 'required_by_date']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = SDRRequest.objects.select_related(
            'raised_by', 'assigned_to', 'assigned_by', 'closed_by'
        ).prefetch_related('responses', 'attachments')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return SDRRequestListSerializer
        return SDRRequestDetailSerializer

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user, status='DRAFT')

    # ---- Workflow: submit -------------------------------------------------
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status != 'DRAFT':
            return Response({'error': 'Only DRAFT SDRs can be submitted.'}, status=400)
        sdr.status = 'SUBMITTED'
        sdr.save(update_fields=['status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    # ---- Workflow: assign -------------------------------------------------
    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status not in ('SUBMITTED', 'ESCALATED'):
            return Response({'error': 'SDR must be SUBMITTED or ESCALATED to assign.'}, status=400)
        assigned_to_id      = request.data.get('assigned_to')
        target_date         = request.data.get('target_response_date')
        if not assigned_to_id:
            return Response({'error': 'assigned_to user ID is required.'}, status=400)
        sdr.assigned_to_id      = assigned_to_id
        sdr.assigned_by         = request.user
        sdr.assigned_at         = timezone.now()
        sdr.target_response_date= target_date
        sdr.status              = 'ASSIGNED'
        sdr.save(update_fields=[
            'assigned_to_id', 'assigned_by', 'assigned_at',
            'target_response_date', 'status', 'updated_at'
        ])
        return Response(SDRRequestDetailSerializer(sdr).data)

    # ---- Workflow: start --------------------------------------------------
    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status != 'ASSIGNED':
            return Response({'error': 'SDR must be ASSIGNED to start work.'}, status=400)
        sdr.status = 'IN_PROGRESS'
        sdr.save(update_fields=['status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    # ---- Workflow: respond ------------------------------------------------
    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status not in ('IN_PROGRESS', 'ASSIGNED'):
            return Response({'error': 'SDR must be IN_PROGRESS or ASSIGNED to respond.'}, status=400)

        ser = SDRResponseSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        response_obj = ser.save(
            sdr_request=sdr,
            responded_by=request.user
        )

        # Only mark RESPONDED for FINAL response
        if response_obj.response_type == 'FINAL':
            sdr.status = 'RESPONDED'
            sdr.save(update_fields=['status', 'updated_at'])

        return Response(SDRResponseSerializer(response_obj).data, status=201)

    # ---- Workflow: close --------------------------------------------------
    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status not in ('RESPONDED', 'IN_PROGRESS'):
            return Response({'error': 'SDR must be RESPONDED to close.'}, status=400)
        sdr.closed_by       = request.user
        sdr.closed_at       = timezone.now()
        sdr.closure_remarks = request.data.get('closure_remarks', '')
        sdr.shop_satisfaction = request.data.get('shop_satisfaction')
        sdr.status          = 'CLOSED'
        sdr.save(update_fields=['closed_by', 'closed_at', 'closure_remarks', 'shop_satisfaction', 'status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    # ---- Workflow: escalate -----------------------------------------------
    @action(detail=True, methods=['post'], url_path='escalate')
    def escalate(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status in ('CLOSED', 'REJECTED'):
            return Response({'error': 'Cannot escalate a CLOSED or REJECTED SDR.'}, status=400)
        sdr.status = 'ESCALATED'
        sdr.save(update_fields=['status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    # ---- Workflow: reject -------------------------------------------------
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status not in ('SUBMITTED', 'ASSIGNED', 'DRAFT'):
            return Response({'error': 'Cannot reject SDR in current status.'}, status=400)
        sdr.rejection_reason = request.data.get('rejection_reason', '')
        sdr.status           = 'REJECTED'
        sdr.save(update_fields=['rejection_reason', 'status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    # ---- List views -------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='my-requests')
    def my_requests(self, request):
        qs = self.get_queryset().filter(raised_by=request.user)
        serializer = SDRRequestListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='pending-action')
    def pending_action(self, request):
        qs = self.get_queryset().filter(
            assigned_to=request.user,
            status__in=['ASSIGNED', 'IN_PROGRESS', 'ESCALATED']
        )
        serializer = SDRRequestListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        from datetime import date
        qs = self.get_queryset().filter(
            target_response_date__lt=date.today(),
            status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'ESCALATED']
        )
        serializer = SDRRequestListSerializer(qs, many=True)
        return Response(serializer.data)


class SDRResponseViewSet(viewsets.ModelViewSet):
    queryset           = SDRResponse.objects.select_related('responded_by', 'sdr_request')
    serializer_class   = SDRResponseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['sdr_request', 'response_type']

    def perform_create(self, serializer):
        serializer.save(responded_by=self.request.user)


class SDRAttachmentViewSet(viewsets.ModelViewSet):
    queryset           = SDRAttachment.objects.select_related('uploaded_by', 'sdr_request')
    serializer_class   = SDRAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['sdr_request', 'attached_to_type']

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('file')
        serializer.save(
            uploaded_by=self.request.user,
            file_name=file_obj.name if file_obj else '',
            file_size=file_obj.size if file_obj else 0,
        )
