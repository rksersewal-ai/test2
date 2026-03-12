"""Tests for dashboard stats endpoint."""
import pytest


@pytest.mark.django_db
class TestDashboardStats:
    def test_stats_authenticated(self, auth_client_engineer):
        resp = auth_client_engineer.get('/api/v1/dashboard/stats/')
        assert resp.status_code == 200
        assert 'documents' in resp.data
        assert 'work_ledger' in resp.data
        assert 'ocr_queue' in resp.data
        assert 'generated_at' in resp.data

    def test_stats_unauthenticated(self, api_client):
        resp = api_client.get('/api/v1/dashboard/stats/')
        assert resp.status_code == 401

    def test_stats_document_counts(self, auth_client_engineer):
        resp = auth_client_engineer.get('/api/v1/dashboard/stats/')
        doc_stats = resp.data['documents']
        assert 'total' in doc_stats
        assert 'active' in doc_stats
