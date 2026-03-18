"""Dashboard stats endpoint tests — PRD Section 17."""
import pytest
from apps.workflow.models import ApprovalChain, ApprovalRequest
from tests.factories import (
    DocumentFactory,
    OCRQueueFactory,
    RevisionFactory,
    WorkLedgerEntryFactory,
)

URL = '/api/v1/dashboard/stats/'


@pytest.mark.django_db
class TestDashboardStats:
    def test_requires_auth(self, api_client):
        r = api_client.get(URL)
        assert r.status_code == 401

    def test_returns_200_for_engineer(self, auth_client_engineer):
        r = auth_client_engineer.get(URL)
        assert r.status_code == 200

    def test_response_shape(self, auth_client_engineer):
        r = auth_client_engineer.get(URL)
        data = r.data
        assert 'generated_at' in data
        assert 'stats' in data
        assert 'documents' in data
        assert 'work_ledger' in data
        assert 'ocr_queue' in data
        assert 'documents_by_section' in data
        assert 'recent_docs' in data
        assert 'pending_approvals' in data

    def test_document_counts_correct(self, auth_client_engineer):
        DocumentFactory.create_batch(2, status='ACTIVE')
        DocumentFactory.create_batch(1, status='DRAFT')
        r = auth_client_engineer.get(URL)
        assert r.data['documents']['active'] >= 2
        assert r.data['documents']['draft'] >= 1
        assert r.data['documents']['total'] >= 3

    def test_work_ledger_counts_correct(self, auth_client_engineer):
        WorkLedgerEntryFactory.create_batch(3, status='OPEN')
        r = auth_client_engineer.get(URL)
        assert r.data['work_ledger']['open'] >= 3

    def test_recent_docs_and_pending_approvals_are_included(self, auth_client_engineer, engineer_user):
        document = DocumentFactory(created_by=engineer_user, title='Dashboard Pending Document')
        revision = RevisionFactory(document=document, created_by=engineer_user)
        chain = ApprovalChain.objects.create(name='Default Dashboard Chain', created_by=engineer_user)
        ApprovalRequest.objects.create(
            chain=chain,
            revision=revision,
            status=ApprovalRequest.Status.PENDING,
            initiated_by=engineer_user,
        )

        r = auth_client_engineer.get(URL)

        assert any(item['id'] == document.id for item in r.data['recent_docs'])
        assert any(item['id'] == document.id for item in r.data['pending_approvals'])
        assert r.data['stats']['pending_approvals'] >= 1
