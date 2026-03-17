# =============================================================================
# FILE: apps/work_ledger/views.py
# Consistent DRF views for the active Work Ledger app.
# =============================================================================
import csv
from datetime import date as dt_date

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WorkCategory, WorkEntry, WorkStatus, WorkTarget, WorkVerification
from .serializers import (
    WorkCategorySerializer,
    WorkEntryReadSerializer,
    WorkEntryWriteSerializer,
    WorkTargetSerializer,
)


STATUS_ALIASES = {
    'OPEN': WorkStatus.DRAFT,
    'PENDING': WorkStatus.SUBMITTED,
    'CLOSED': WorkStatus.APPROVED,
}


def _display_name(user) -> str:
    return (
        getattr(user, 'full_name', '')
        or getattr(user, 'get_full_name', lambda: '')()
        or user.username
    )


def _is_supervisor(user) -> bool:
    return bool(user.is_staff or getattr(user, 'is_supervisor', False))


def _base_entry_queryset():
    return WorkEntry.objects.select_related('user', 'user__section', 'category', 'submitted_to')


def _apply_activity_filters(queryset, params):
    from_date = parse_date(params.get('from_date', ''))
    to_date = parse_date(params.get('to_date', ''))
    section = (params.get('section') or '').strip()
    engineer_id = params.get('engineer_id')
    officer_id = params.get('officer_id')
    category = (params.get('category') or '').strip()
    pl_number = (params.get('pl_number') or '').strip()
    status = (params.get('status') or '').strip().upper()

    if from_date:
        queryset = queryset.filter(work_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(work_date__lte=to_date)
    if section:
        queryset = queryset.filter(user__section__name__iexact=section)
    if engineer_id:
        queryset = queryset.filter(user_id=engineer_id)
    if officer_id:
        queryset = queryset.filter(submitted_to_id=officer_id)
    if category:
        queryset = queryset.filter(category__code=category)
    if pl_number:
        queryset = queryset.filter(linked_pl_number_id=pl_number)
    if status:
        queryset = queryset.filter(status=STATUS_ALIASES.get(status, status))

    return queryset


class WorkCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkCategory.objects.filter(is_active=True).order_by('sort_order', 'name')
    serializer_class = WorkCategorySerializer
    permission_classes = [IsAuthenticated]


class WorkEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'work_type', 'category', 'work_date', 'priority']
    search_fields = [
        'description',
        'reference_number',
        'linked_drawing_number',
        'linked_case_no',
        'linked_sdr_no',
    ]
    ordering_fields = ['work_date', 'created_at', 'updated_at', 'status']
    ordering = ['-work_date', '-created_at']

    def get_queryset(self):
        queryset = (
            WorkEntry.objects.select_related('user', 'category', 'submitted_to')
            .prefetch_related('verifications', 'attachments')
            .all()
        )
        if _is_supervisor(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return WorkEntryWriteSerializer
        return WorkEntryReadSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        entry = self.get_object()
        if entry.user_id != request.user.id and not _is_supervisor(request.user):
            return Response({'error': 'Access denied.'}, status=403)
        if not entry.can_submit():
            return Response({'error': 'Only DRAFT or RETURNED entries can be submitted.'}, status=400)

        supervisor_id = request.data.get('supervisor_id')
        supervisor = request.user
        if supervisor_id:
            supervisor = get_user_model().objects.filter(pk=supervisor_id).first()
            if supervisor is None:
                return Response({'error': 'Supervisor not found.'}, status=404)

        entry.submit(supervisor=supervisor)
        return Response(WorkEntryReadSerializer(entry, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        entry = self.get_object()
        if not _is_supervisor(request.user):
            return Response({'error': 'Access denied.'}, status=403)
        if not entry.can_verify():
            return Response({'error': 'Only SUBMITTED entries can be verified.'}, status=400)

        raw_action = str(request.data.get('action', 'VERIFIED')).strip().upper()
        remarks = request.data.get('remarks', '')

        if raw_action in {'RETURN', 'RETURNED', 'REJECT'}:
            entry.return_for_correction(request.user, remarks)
        else:
            if raw_action in {'APPROVE', 'APPROVED'}:
                verification_action = WorkVerification.Action.APPROVED
                entry.status = 'APPROVED'
            else:
                verification_action = WorkVerification.Action.VERIFIED
                entry.status = 'VERIFIED'
            WorkVerification.objects.create(
                work_entry=entry,
                verifier=request.user,
                action=verification_action,
                remarks=remarks,
            )
            entry.save(update_fields=['status'])

        entry.refresh_from_db()
        return Response(WorkEntryReadSerializer(entry, context={'request': request}).data)

    @action(detail=False, methods=['get'], url_path='my-entries')
    def my_entries(self, request):
        queryset = self.get_queryset().filter(user=request.user)
        serializer = WorkEntryReadSerializer(
            queryset,
            many=True,
            context={'request': request},
        )
        return Response(
            {
                'count': queryset.count(),
                'entries': serializer.data,
                'status_counts': {
                    status: queryset.filter(status=status).count()
                    for status in ('DRAFT', 'SUBMITTED', 'VERIFIED', 'APPROVED', 'RETURNED')
                },
            }
        )


class WorkTargetViewSet(viewsets.ModelViewSet):
    serializer_class = WorkTargetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = WorkTarget.objects.select_related('user', 'set_by').all()
        if _is_supervisor(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(set_by=self.request.user)


class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', dt_date.today().year))
        month = int(request.query_params.get('month', dt_date.today().month))
        fmt = str(request.query_params.get('format', 'pdf')).lower()
        uid = request.query_params.get('user_id')

        target = self._resolve_user(request, uid)
        if isinstance(target, Response):
            return target

        if fmt == 'xlsx':
            from .reports_excel import generate_monthly_work_report_excel

            xlsx_bytes = generate_monthly_work_report_excel(target, year, month)
            return self._xlsx_response(target, year, month, xlsx_bytes)

        from .reports import generate_monthly_work_report

        pdf_bytes = generate_monthly_work_report(target, year, month)
        return self._pdf_response(target, year, month, pdf_bytes)

    def _resolve_user(self, request, uid):
        if uid and _is_supervisor(request.user):
            user = get_user_model().objects.filter(pk=uid).first()
            if user is None:
                return Response({'error': 'User not found.'}, status=404)
            return user
        return request.user

    def _pdf_response(self, user, year: int, month: int, content: bytes):
        month_str = f'{year}-{month:02d}'
        name_slug = _display_name(user).replace(' ', '_')
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="WorkReport_{name_slug}_{month_str}.pdf"'
        )
        return response

    def _xlsx_response(self, user, year: int, month: int, content: bytes):
        month_str = f'{year}-{month:02d}'
        name_slug = _display_name(user).replace(' ', '_')
        response = HttpResponse(
            content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = (
            f'attachment; filename="WorkReport_{name_slug}_{month_str}.xlsx"'
        )
        return response


class MonthlyExcelReportView(MonthlyReportView):
    def get(self, request):
        year = int(request.query_params.get('year', dt_date.today().year))
        month = int(request.query_params.get('month', dt_date.today().month))
        uid = request.query_params.get('user_id')

        target = self._resolve_user(request, uid)
        if isinstance(target, Response):
            return target

        from .reports_excel import generate_monthly_work_report_excel

        xlsx_bytes = generate_monthly_work_report_excel(target, year, month)
        return self._xlsx_response(target, year, month, xlsx_bytes)


class MonthlyKPIReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', dt_date.today().year))
        month = int(request.query_params.get('month', dt_date.today().month))
        section = (request.query_params.get('section') or '').strip()

        queryset = _base_entry_queryset().filter(
            work_date__year=year,
            work_date__month=month,
        )
        if section:
            queryset = queryset.filter(user__section__name__iexact=section)
        if not _is_supervisor(request.user):
            queryset = queryset.filter(user=request.user)

        summary = list(
            queryset.values('category__code', 'category__name')
            .annotate(work_count=Count('id'))
            .order_by('category__sort_order', 'category__name')
        )
        return Response(
            {
                'month': f'{year}-{month:02d}',
                'summary': [
                    {
                        'work_category_code': row['category__code'] or 'UNCATEGORISED',
                        'work_category_label': row['category__name'] or 'Uncategorised',
                        'work_count': row['work_count'],
                    }
                    for row in summary
                ],
            }
        )


class WorkActivityReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = _apply_activity_filters(
            _base_entry_queryset().prefetch_related('attachments', 'verifications').order_by(
                '-work_date',
                '-created_at',
            ),
            request.query_params,
        )
        if not _is_supervisor(request.user):
            queryset = queryset.filter(user=request.user)

        serializer = WorkEntryReadSerializer(
            queryset,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


class WorkActivityReportExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = _apply_activity_filters(
            _base_entry_queryset().order_by('-work_date', '-created_at'),
            request.query_params,
        )
        if not _is_supervisor(request.user):
            queryset = queryset.filter(user=request.user)

        rows = WorkEntryReadSerializer(
            queryset,
            many=True,
            context={'request': request},
        ).data

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="work_activity_report.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                'Work Code',
                'Date',
                'Section',
                'Category',
                'Description',
                'PL Number',
                'Drawing Number',
                'Tender/Case Number',
                'Status',
                'Remarks',
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.get('work_code', ''),
                    row.get('received_date', ''),
                    row.get('section', ''),
                    row.get('work_category_label', ''),
                    row.get('description', ''),
                    row.get('pl_number', ''),
                    row.get('drawing_number', ''),
                    row.get('tender_number', ''),
                    row.get('status', ''),
                    row.get('remarks', ''),
                ]
            )
        return response
