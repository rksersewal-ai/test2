"""Dashboard stats endpoint tests — PRD Section 17."""
import pytest
from tests.factories import DocumentFactory, WorkLedgerEntryFactory, OCRQueueFactory

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
        assert 'documents' in data
        assert 'work_ledger' in data
        assert 'ocr_queue' in data
        assert 'documents_by_section' in data

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
