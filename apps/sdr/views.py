# =============================================================================
# FILE: apps/sdr/views.py  (updated — added AnalyticsView)
# =============================================================================
from datetime import date, timedelta

from django.db.models            import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.utils                import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators  import action
from rest_framework.response    import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views       import APIView

from .models       import SDRRequest, SDRResponse, SDRAttachment
from .serializers  import (
    SDRRequestListSerializer, SDRRequestDetailSerializer,
    SDRResponseSerializer, SDRAttachmentSerializer,
)


# ===========================================================================
class SDRRequestViewSet(viewsets.ModelViewSet):
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
        return SDRRequest.objects.select_related(
            'raised_by', 'assigned_to', 'assigned_by', 'closed_by'
        ).prefetch_related('responses', 'attachments')

    def get_serializer_class(self):
        return SDRRequestListSerializer if self.action == 'list' else SDRRequestDetailSerializer

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user, status='DRAFT')

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status != 'DRAFT':
            return Response({'error': 'Only DRAFT SDRs can be submitted.'}, status=400)
        sdr.status = 'SUBMITTED'
        sdr.save(update_fields=['status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status not in ('SUBMITTED', 'ESCALATED'):
            return Response({'error': 'SDR must be SUBMITTED or ESCALATED to assign.'}, status=400)
        assigned_to_id = request.data.get('assigned_to')
        if not assigned_to_id:
            return Response({'error': 'assigned_to is required.'}, status=400)
        sdr.assigned_to_id       = assigned_to_id
        sdr.assigned_by          = request.user
        sdr.assigned_at          = timezone.now()
        sdr.target_response_date = request.data.get('target_response_date')
        sdr.status               = 'ASSIGNED'
        sdr.save(update_fields=[
            'assigned_to_id','assigned_by','assigned_at','target_response_date','status','updated_at'
        ])
        return Response(SDRRequestDetailSerializer(sdr).data)

    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status != 'ASSIGNED':
            return Response({'error': 'SDR must be ASSIGNED to start.'}, status=400)
        sdr.status = 'IN_PROGRESS'
        sdr.save(update_fields=['status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status not in ('IN_PROGRESS', 'ASSIGNED'):
            return Response({'error': 'SDR must be IN_PROGRESS or ASSIGNED to respond.'}, status=400)
        ser = SDRResponseSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        resp_obj = ser.save(sdr_request=sdr, responded_by=request.user)
        if resp_obj.response_type == 'FINAL':
            sdr.status = 'RESPONDED'
            sdr.save(update_fields=['status', 'updated_at'])
        return Response(SDRResponseSerializer(resp_obj).data, status=201)

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status not in ('RESPONDED', 'IN_PROGRESS'):
            return Response({'error': 'SDR must be RESPONDED to close.'}, status=400)
        sdr.closed_by        = request.user
        sdr.closed_at        = timezone.now()
        sdr.closure_remarks  = request.data.get('closure_remarks', '')
        sdr.shop_satisfaction= request.data.get('shop_satisfaction')
        sdr.status           = 'CLOSED'
        sdr.save(update_fields=['closed_by','closed_at','closure_remarks','shop_satisfaction','status','updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    @action(detail=True, methods=['post'], url_path='escalate')
    def escalate(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status in ('CLOSED', 'REJECTED'):
            return Response({'error': 'Cannot escalate a CLOSED or REJECTED SDR.'}, status=400)
        sdr.status = 'ESCALATED'
        sdr.save(update_fields=['status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        sdr = self.get_object()
        if sdr.status not in ('SUBMITTED', 'ASSIGNED', 'DRAFT'):
            return Response({'error': 'Cannot reject SDR in current status.'}, status=400)
        sdr.rejection_reason = request.data.get('rejection_reason', '')
        sdr.status           = 'REJECTED'
        sdr.save(update_fields=['rejection_reason', 'status', 'updated_at'])
        return Response(SDRRequestDetailSerializer(sdr).data)

    @action(detail=False, methods=['get'], url_path='my-requests')
    def my_requests(self, request):
        qs = self.get_queryset().filter(raised_by=request.user)
        return Response(SDRRequestListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='pending-action')
    def pending_action(self, request):
        qs = self.get_queryset().filter(
            assigned_to=request.user,
            status__in=['ASSIGNED', 'IN_PROGRESS', 'ESCALATED']
        )
        return Response(SDRRequestListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        qs = self.get_queryset().filter(
            target_response_date__lt=date.today(),
            status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'ESCALATED']
        )
        return Response(SDRRequestListSerializer(qs, many=True).data)


# ===========================================================================
class SDRResponseViewSet(viewsets.ModelViewSet):
    queryset           = SDRResponse.objects.select_related('responded_by', 'sdr_request')
    serializer_class   = SDRResponseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['sdr_request', 'response_type']

    def perform_create(self, serializer):
        serializer.save(responded_by=self.request.user)


# ===========================================================================
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


# ===========================================================================
class SDRAnalyticsView(APIView):
    """
    GET /api/v1/sdr/analytics/

    Returns:
      - status_counts         : {status: count}
      - by_section            : [{raising_section, count}]
      - by_urgency            : [{urgency, count}]
      - by_clarification_type : [{clarification_type, count}]
      - production_hold_open  : count
      - avg_tat_days          : average turnaround (CLOSED SDRs, created → closed)
      - avg_satisfaction      : average shop satisfaction (1-5)
      - top_drawing_numbers   : top 10 most-queried drawings
      - overdue_count         : SDRs past target_response_date
      - period_trend          : last 30 days, daily submission count
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today   = date.today()
        base_qs = SDRRequest.objects.all()

        # Status counts
        status_counts = {
            row['status']: row['cnt']
            for row in base_qs.values('status').annotate(cnt=Count('id'))
        }

        # By section
        by_section = list(
            base_qs.values('raising_section')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # By urgency
        by_urgency = list(
            base_qs.values('urgency')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # By clarification type
        by_ctype = list(
            base_qs.values('clarification_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Production hold open
        prod_hold_open = base_qs.filter(
            production_hold=True,
            status__in=['SUBMITTED','ASSIGNED','IN_PROGRESS','ESCALATED']
        ).count()

        # Avg TAT (closed SDRs)
        closed = base_qs.filter(status='CLOSED', closed_at__isnull=False)
        avg_tat = None
        if closed.exists():
            durations = [
                (s.closed_at.date() - s.created_at.date()).days
                for s in closed.only('created_at', 'closed_at')
                if s.closed_at
            ]
            avg_tat = round(sum(durations) / len(durations), 1) if durations else None

        # Avg satisfaction
        from django.db.models import Avg as DjAvg
        avg_sat = closed.aggregate(avg=DjAvg('shop_satisfaction'))['avg']
        if avg_sat:
            avg_sat = round(float(avg_sat), 2)

        # Top queried drawings
        top_drawings = list(
            base_qs.exclude(drawing_number='')
            .values('drawing_number')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Overdue
        overdue_count = base_qs.filter(
            target_response_date__lt=today,
            status__in=['SUBMITTED','ASSIGNED','IN_PROGRESS','ESCALATED']
        ).count()

        # 30-day trend
        trend_start = today - timedelta(days=29)
        trend_qs    = (
            base_qs
            .filter(created_at__date__gte=trend_start)
            .values('created_at__date')
            .annotate(count=Count('id'))
            .order_by('created_at__date')
        )
        period_trend = [
            {'date': str(row['created_at__date']), 'count': row['count']}
            for row in trend_qs
        ]

        return Response({
            'status_counts':         status_counts,
            'by_section':            by_section,
            'by_urgency':            by_urgency,
            'by_clarification_type': by_ctype,
            'production_hold_open':  prod_hold_open,
            'avg_tat_days':          avg_tat,
            'avg_satisfaction':      avg_sat,
            'top_drawing_numbers':   top_drawings,
            'overdue_count':         overdue_count,
            'period_trend':          period_trend,
        })
