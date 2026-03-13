import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from .models import WorkLedger, WorkCategoryMaster
from .serializers import (
    WorkLedgerWriteSerializer,
    WorkLedgerListSerializer,
    WorkLedgerDetailReadSerializer,
    WorkCategorySerializer,
    KpiSummaryRowSerializer,
    ActivityReportRowSerializer,
)
from .services import create_work_entry, update_work_entry
from .repositories import get_activity_report, get_monthly_kpi, get_dashboard_monthly_summary
from .reporting import build_csv_response, ACTIVITY_REPORT_FIELDS
from .permissions import CanCreateWorkEntry, CanEditWorkEntry, CanExportReports


class WorkCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cats = WorkCategoryMaster.objects.filter(is_active=True)
        return Response(WorkCategorySerializer(cats, many=True).data)


class WorkLedgerListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WorkLedger.objects.all()
        section = request.query_params.get("section")
        status_filter = request.query_params.get("status")
        engineer_id = request.query_params.get("engineer_id")
        if section:
            qs = qs.filter(section=section)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if engineer_id:
            qs = qs.filter(engineer_id=engineer_id)
        return Response(WorkLedgerListSerializer(qs, many=True).data)

    def post(self, request):
        self.check_permissions(request)
        perm = CanCreateWorkEntry()
        if not perm.has_permission(request, self):
            return Response({"detail": "Insufficient role."}, status=403)
        serializer = WorkLedgerWriteSerializer(data=request.data)
        if serializer.is_valid():
            entry = create_work_entry(serializer.validated_data, created_by=request.user.id)
            return Response(
                WorkLedgerDetailReadSerializer(entry).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkLedgerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_entry(self, work_id):
        try:
            return WorkLedger.objects.get(pk=work_id)
        except WorkLedger.DoesNotExist:
            return None

    def get(self, request, work_id):
        entry = self._get_entry(work_id)
        if not entry:
            return Response({"detail": "Not found."}, status=404)
        return Response(WorkLedgerDetailReadSerializer(entry).data)

    def put(self, request, work_id):
        entry = self._get_entry(work_id)
        if not entry:
            return Response({"detail": "Not found."}, status=404)
        perm = CanEditWorkEntry()
        if not perm.has_object_permission(request, self, entry):
            return Response({"detail": "Insufficient role."}, status=403)
        serializer = WorkLedgerWriteSerializer(data=request.data)
        if serializer.is_valid():
            updated = update_work_entry(entry, serializer.validated_data)
            return Response(WorkLedgerDetailReadSerializer(updated).data)
        return Response(serializer.errors, status=400)


class WorkLedgerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        year = int(request.query_params.get("year", today.year))
        month = int(request.query_params.get("month", today.month))
        data = get_dashboard_monthly_summary(year, month)
        return Response(data)


class WorkActivityReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = get_activity_report(
            from_date=request.query_params.get("from_date"),
            to_date=request.query_params.get("to_date"),
            section=request.query_params.get("section"),
            engineer_id=request.query_params.get("engineer_id"),
            officer_id=request.query_params.get("officer_id"),
            category_code=request.query_params.get("category"),
            pl_number=request.query_params.get("pl_number"),
            status=request.query_params.get("status"),
        )
        return Response(rows)


class WorkMonthlyKpiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        year = int(request.query_params.get("year", today.year))
        month = int(request.query_params.get("month", today.month))
        section = request.query_params.get("section")
        rows = get_monthly_kpi(year, month, section)
        return Response(
            {"month": f"{year}-{month:02d}", "summary": rows}
        )


class WorkActivityReportExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        perm = CanExportReports()
        if not perm.has_permission(request, self):
            return Response({"detail": "Insufficient role."}, status=403)
        fmt = request.query_params.get("format", "csv").lower()
        rows = get_activity_report(
            from_date=request.query_params.get("from_date"),
            to_date=request.query_params.get("to_date"),
            section=request.query_params.get("section"),
            engineer_id=request.query_params.get("engineer_id"),
            officer_id=request.query_params.get("officer_id"),
            category_code=request.query_params.get("category"),
            pl_number=request.query_params.get("pl_number"),
            status=request.query_params.get("status"),
        )
        if fmt == "csv":
            csv_data = build_csv_response(rows, ACTIVITY_REPORT_FIELDS)
            response = HttpResponse(csv_data, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="work_activity_report.csv"'
            return response
        # xlsx and pdf export stubs – extend with openpyxl / reportlab
        return Response({"detail": f"Format '{fmt}' not yet implemented."}, status=501)
