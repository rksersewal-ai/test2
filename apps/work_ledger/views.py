# =============================================================================
# FILE: apps/work_ledger/views.py  (updated — PDF + Excel report endpoints)
# =============================================================================
from datetime import date as dt_date

from django.http              import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators  import action
from rest_framework.response    import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views       import APIView

from .models      import WorkEntry, WorkCategory, WorkTarget
from .serializers import (
    WorkEntrySerializer, WorkCategorySerializer,
    WorkTargetSerializer, WorkEntryCreateSerializer,
)
from .reports       import generate_monthly_work_report
from .reports_excel import generate_monthly_work_report_excel


class WorkCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = WorkCategory.objects.filter(is_active=True).order_by('category_name')
    serializer_class   = WorkCategorySerializer
    permission_classes = [IsAuthenticated]


class WorkEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status', 'work_type', 'category', 'work_date']
    search_fields      = ['work_description', 'reference_number', 'eoffice_file_no']
    ordering_fields    = ['work_date', 'created_at', 'status']
    ordering           = ['-work_date']

    def get_queryset(self):
        user = self.request.user
        qs   = WorkEntry.objects.select_related('category', 'created_by', 'verified_by')
        if not getattr(user, 'is_supervisor', False) and not user.is_staff:
            qs = qs.filter(created_by=user)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return WorkEntryCreateSerializer
        return WorkEntrySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        entry = self.get_object()
        if entry.status != 'DRAFT':
            return Response({'error': 'Only DRAFT entries can be submitted.'}, status=400)
        entry.status = 'SUBMITTED'
        entry.save(update_fields=['status', 'updated_at'])
        return Response(WorkEntrySerializer(entry).data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        entry     = self.get_object()
        act       = request.data.get('action', 'VERIFY')
        if entry.status != 'SUBMITTED':
            return Response({'error': 'Only SUBMITTED entries can be verified.'}, status=400)
        if act == 'RETURN':
            entry.status           = 'RETURNED'
            entry.verifier_remarks = request.data.get('remarks', '')
        else:
            entry.status           = 'VERIFIED'
            entry.verified_by      = request.user
            entry.verified_at      = dt_date.today()
            entry.verifier_remarks = request.data.get('remarks', '')
        entry.save()
        return Response(WorkEntrySerializer(entry).data)

    @action(detail=False, methods=['get'], url_path='my-entries')
    def my_entries(self, request):
        qs = WorkEntry.objects.filter(created_by=request.user).select_related('category','verified_by')
        return Response({
            'count':   qs.count(),
            'entries': WorkEntrySerializer(qs, many=True).data,
            'status_counts': {
                s: qs.filter(status=s).count()
                for s in ('DRAFT','SUBMITTED','VERIFIED','APPROVED','RETURNED')
            }
        })

    @action(detail=False, methods=['get'], url_path='team-summary')
    def team_summary(self, request):
        if not (request.user.is_staff or getattr(request.user, 'is_supervisor', False)):
            return Response({'error': 'Access denied.'}, status=403)
        from django.db.models import Count, Sum
        summary = (
            WorkEntry.objects
            .values('created_by__id','created_by__first_name','created_by__last_name')
            .annotate(total=Count('id'), hours=Sum('hours_spent'))
            .order_by('-total')
        )
        return Response(list(summary))


class WorkTargetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return WorkTarget.objects.all() if user.is_staff else WorkTarget.objects.filter(user=user)

    def get_serializer_class(self):
        return WorkTargetSerializer


class MonthlyReportView(APIView):
    """
    GET /api/v1/work/report/?year=2026&month=3
    GET /api/v1/work/report/?year=2026&month=3&user_id=42   (supervisors only)
    Returns PDF.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year  = int(request.query_params.get('year',  dt_date.today().year))
        month = int(request.query_params.get('month', dt_date.today().month))
        uid   = request.query_params.get('user_id')

        target = self._resolve_user(request, uid)
        if isinstance(target, Response):
            return target

        try:
            pdf_bytes = generate_monthly_work_report(target, year, month)
        except ImportError as exc:
            return Response({'error': str(exc)}, status=500)

        month_str = f'{year}-{month:02d}'
        name_slug = (target.get_full_name() or target.username).replace(' ', '_')
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="WorkReport_{name_slug}_{month_str}.pdf"'
        return resp

    def _resolve_user(self, request, uid):
        if uid and (request.user.is_staff or getattr(request.user, 'is_supervisor', False)):
            from django.contrib.auth import get_user_model
            try:
                return get_user_model().objects.get(pk=uid)
            except Exception:
                return Response({'error': 'User not found.'}, status=404)
        return request.user


class MonthlyExcelReportView(APIView):
    """
    GET /api/v1/work/report/excel/?year=2026&month=3
    GET /api/v1/work/report/excel/?year=2026&month=3&user_id=42
    Returns .xlsx with 3 sheets: Work Entries / Summary / Targets vs Actual.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year  = int(request.query_params.get('year',  dt_date.today().year))
        month = int(request.query_params.get('month', dt_date.today().month))
        uid   = request.query_params.get('user_id')

        if uid and (request.user.is_staff or getattr(request.user, 'is_supervisor', False)):
            from django.contrib.auth import get_user_model
            try:
                target = get_user_model().objects.get(pk=uid)
            except Exception:
                return Response({'error': 'User not found.'}, status=404)
        else:
            target = request.user

        try:
            xlsx_bytes = generate_monthly_work_report_excel(target, year, month)
        except ImportError as exc:
            return Response({'error': str(exc)}, status=500)

        month_str = f'{year}-{month:02d}'
        name_slug = (target.get_full_name() or target.username).replace(' ', '_')
        resp = HttpResponse(
            xlsx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        resp['Content-Disposition'] = f'attachment; filename="WorkReport_{name_slug}_{month_str}.xlsx"'
        return resp
