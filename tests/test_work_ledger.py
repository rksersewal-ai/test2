"""Active Work Ledger API regression tests."""
from datetime import date

import pytest

from apps.work_ledger.models import WorkCategory, WorkEntry, WorkStatus, WorkType


BASE = '/api/v1/work-ledger/'


@pytest.mark.django_db
class TestWorkLedgerReports:
    def _create_entry(self, user):
        category = WorkCategory.objects.create(
            name='Specification Processing',
            code='SPEC_PROC',
            work_type=WorkType.SPEC_PROCESSING,
        )
        return WorkEntry.objects.create(
            user=user,
            work_date=date(2026, 3, 1),
            category=category,
            work_type=WorkType.SPEC_PROCESSING,
            description='Prepared specification revision package.',
            reference_number='PLW/LDO/2026/001',
            remarks='Ready for verification',
            status=WorkStatus.DRAFT,
        )

    def test_kpi_report_returns_summary(self, auth_client_engineer, engineer_user):
        self._create_entry(engineer_user)
        r = auth_client_engineer.get(BASE + 'report/kpi/', {'year': 2026, 'month': 3})
        assert r.status_code == 200
        assert r.data['month'] == '2026-03'
        assert r.data['summary'][0]['work_category_code'] == 'SPEC_PROC'

    def test_activity_report_returns_entries(self, auth_client_engineer, engineer_user):
        entry = self._create_entry(engineer_user)
        r = auth_client_engineer.get(BASE + 'report/activity/', {'from_date': '2026-03-01', 'to_date': '2026-03-31'})
        assert r.status_code == 200
        assert len(r.data) == 1
        assert r.data[0]['work_id'] == entry.pk

    def test_activity_export_returns_csv(self, auth_client_engineer, engineer_user):
        self._create_entry(engineer_user)
        r = auth_client_engineer.get(BASE + 'report/export/', {'from_date': '2026-03-01', 'to_date': '2026-03-31'})
        assert r.status_code == 200
        assert 'text/csv' in r['Content-Type']
        assert 'Prepared specification revision package.' in r.content.decode('utf-8')

    def test_monthly_report_returns_pdf(self, auth_client_engineer, engineer_user):
        self._create_entry(engineer_user)
        r = auth_client_engineer.get(BASE + 'report/', {'year': 2026, 'month': 3})
        assert r.status_code == 200
        assert 'application/pdf' in r['Content-Type']
        assert len(r.content) > 0

    def test_monthly_excel_report_returns_xlsx(self, auth_client_engineer, engineer_user):
        self._create_entry(engineer_user)
        r = auth_client_engineer.get(BASE + 'report/excel/', {'year': 2026, 'month': 3})
        assert r.status_code == 200
        assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in r['Content-Type']
        assert len(r.content) > 0
