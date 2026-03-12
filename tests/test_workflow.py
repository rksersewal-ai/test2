"""Work Ledger API tests — PRD Section 16."""
import pytest
from tests.factories import WorkLedgerEntryFactory, WorkTypeFactory, SectionFactory

BASE = '/api/v1/workflow/'


@pytest.mark.django_db
class TestWorkTypeList:
    def test_list_work_types(self, auth_client_engineer):
        WorkTypeFactory.create_batch(3)
        r = auth_client_engineer.get(BASE + 'work-types/')
        assert r.status_code == 200
        assert r.data['count'] >= 3


@pytest.mark.django_db
class TestWorkLedgerCreate:
    def test_create_entry(self, auth_client_engineer, engineer_user):
        wt = WorkTypeFactory.create()
        sec = SectionFactory.create()
        payload = {
            'subject': 'WAG9 Drawing Revision - Pantograph',
            'status': 'OPEN',
            'work_type': wt.pk,
            'section': sec.pk,
            'eoffice_file_number': 'PLW/LDO/2026/001',
            'received_date': '2026-03-01',
            'target_date': '2026-04-01',
        }
        r = auth_client_engineer.post(BASE + 'work-ledger/', payload, format='json')
        assert r.status_code == 201
        assert r.data['subject'] == 'WAG9 Drawing Revision - Pantograph'

    def test_viewer_cannot_create(self, auth_client_viewer):
        wt = WorkTypeFactory.create()
        sec = SectionFactory.create()
        r = auth_client_viewer.post(BASE + 'work-ledger/', {
            'subject': 'Blocked', 'status': 'OPEN',
            'work_type': wt.pk, 'section': sec.pk,
        }, format='json')
        assert r.status_code == 403

    def test_unauthenticated_blocked(self, api_client):
        r = api_client.get(BASE + 'work-ledger/')
        assert r.status_code == 401


@pytest.mark.django_db
class TestWorkLedgerFilter:
    def test_filter_by_status(self, auth_client_engineer):
        WorkLedgerEntryFactory.create(status='OPEN')
        WorkLedgerEntryFactory.create(status='CLOSED')
        r = auth_client_engineer.get(BASE + 'work-ledger/', {'status': 'OPEN'})
        assert r.status_code == 200
        for item in r.data['results']:
            assert item['status'] == 'OPEN'

    def test_filter_overdue(self, auth_client_engineer):
        from datetime import date, timedelta
        WorkLedgerEntryFactory.create(
            status='OPEN',
            target_date=date.today() - timedelta(days=10)
        )
        r = auth_client_engineer.get(BASE + 'work-ledger/', {'overdue': 'true'})
        assert r.status_code == 200
        assert r.data['count'] >= 1


@pytest.mark.django_db
class TestWorkLedgerStatusClose:
    def test_close_entry(self, auth_client_admin):
        entry = WorkLedgerEntryFactory.create(status='IN_PROGRESS')
        url = f'/api/v1/workflow/work-ledger/{entry.pk}/'
        r = auth_client_admin.patch(url, {'status': 'CLOSED'}, format='json')
        assert r.status_code == 200
        entry.refresh_from_db()
        assert entry.status == 'CLOSED'
