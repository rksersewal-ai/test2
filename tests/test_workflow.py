"""Tests for apps.workflow: WorkLedger, Tender, Vendor."""
import pytest
from apps.workflow.models import WorkLedger, WorkType, Tender
from apps.edms.models import Document, Category


@pytest.fixture
def work_type(db):
    return WorkType.objects.create(code='LDO-DRG', name='Drawing Preparation')


@pytest.fixture
def work_entry(db, work_type, section, admin_user):
    return WorkLedger.objects.create(
        work_type=work_type,
        section=section,
        subject='Review WAG9 IGBT drawings',
        status=WorkLedger.Status.OPEN,
        eoffice_file_number='EO/2026/PLW/001',
        created_by=admin_user,
    )


@pytest.mark.django_db
class TestWorkLedgerModel:
    def test_work_ledger_str(self, work_entry):
        assert 'WAG9' in str(work_entry)
        assert 'OPEN' in str(work_entry)

    def test_status_transition(self, work_entry):
        work_entry.status = WorkLedger.Status.IN_PROGRESS
        work_entry.save()
        work_entry.refresh_from_db()
        assert work_entry.status == WorkLedger.Status.IN_PROGRESS


@pytest.mark.django_db
class TestWorkLedgerAPI:
    def test_list_work_ledger(self, auth_client_engineer):
        resp = auth_client_engineer.get('/api/v1/workflow/work-ledger/')
        assert resp.status_code == 200

    def test_create_work_entry(self, auth_client_engineer, work_type, section):
        data = {
            'work_type': work_type.id,
            'section': section.id,
            'subject': 'New LDO work item',
            'status': 'OPEN',
            'eoffice_file_number': 'EO/2026/TEST/002',
            'remarks': '',
        }
        resp = auth_client_engineer.post('/api/v1/workflow/work-ledger/', data)
        assert resp.status_code == 201

    def test_filter_by_status(self, auth_client_engineer, work_entry):
        resp = auth_client_engineer.get('/api/v1/workflow/work-ledger/?status=OPEN')
        assert resp.status_code == 200

    def test_search_by_eoffice(self, auth_client_engineer, work_entry):
        resp = auth_client_engineer.get('/api/v1/workflow/work-ledger/?search=PLW/001')
        assert resp.status_code == 200
        assert len(resp.data.get('results', [])) >= 1

    def test_viewer_cannot_create_work_entry(self, auth_client_viewer, work_type, section):
        data = {'work_type': work_type.id, 'section': section.id, 'subject': 'Blocked'}
        resp = auth_client_viewer.post('/api/v1/workflow/work-ledger/', data)
        assert resp.status_code == 403
