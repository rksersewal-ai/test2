"""EDMS API tests — PRD Section 5 & 18."""
import pytest
from django.urls import reverse
from tests.factories import (
    DocumentFactory, RevisionFactory, FileAttachmentFactory,
    SectionFactory, UserFactory,
)


@pytest.mark.django_db
class TestDocumentList:
    url = '/api/v1/edms/documents/'

    def test_list_requires_auth(self, api_client):
        r = api_client.get(self.url)
        assert r.status_code == 401

    def test_list_returns_200_for_engineer(self, auth_client_engineer):
        DocumentFactory.create_batch(3)
        r = auth_client_engineer.get(self.url)
        assert r.status_code == 200
        assert r.data['count'] >= 3

    def test_list_filter_by_status(self, auth_client_engineer):
        DocumentFactory.create(status='ACTIVE')
        DocumentFactory.create(status='DRAFT')
        r = auth_client_engineer.get(self.url, {'status': 'DRAFT'})
        assert r.status_code == 200
        for item in r.data['results']:
            assert item['status'] == 'DRAFT'

    def test_search_by_title(self, auth_client_engineer):
        DocumentFactory.create(title='WAG9 Pantograph Spec')
        r = auth_client_engineer.get(self.url, {'search': 'Pantograph'})
        assert r.status_code == 200
        assert any('Pantograph' in d['title'] for d in r.data['results'])


@pytest.mark.django_db
class TestDocumentCreate:
    url = '/api/v1/edms/documents/'

    def test_engineer_can_create(self, auth_client_engineer, engineer_user, section):
        payload = {
            'doc_number': 'PLW/TEST/2026/9999',
            'title': 'Test Document Created by Engineer',
            'doc_type': 'SPEC',
            'status': 'DRAFT',
            'section': section.pk,
            'language': 'EN',
        }
        r = auth_client_engineer.post(self.url, payload, format='json')
        assert r.status_code == 201
        assert r.data['doc_number'] == 'PLW/TEST/2026/9999'

    def test_viewer_cannot_create(self, auth_client_viewer, section):
        payload = {
            'doc_number': 'PLW/TEST/2026/8888',
            'title': 'Viewer Should Not Create',
            'doc_type': 'SPEC',
            'status': 'DRAFT',
            'section': section.pk,
        }
        r = auth_client_viewer.post(self.url, payload, format='json')
        assert r.status_code == 403

    def test_duplicate_doc_number_rejected(self, auth_client_engineer, section):
        DocumentFactory.create(doc_number='PLW/DUP/0001')
        payload = {
            'doc_number': 'PLW/DUP/0001',
            'title': 'Duplicate',
            'doc_type': 'SPEC',
            'status': 'DRAFT',
            'section': section.pk,
        }
        r = auth_client_engineer.post(self.url, payload, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestDocumentStatusChange:
    def test_change_status_to_obsolete(self, auth_client_admin):
        doc = DocumentFactory.create(status='ACTIVE')
        url = f'/api/v1/edms/documents/{doc.pk}/change-status/'
        r = auth_client_admin.post(url, {'status': 'OBSOLETE'}, format='json')
        assert r.status_code == 200
        doc.refresh_from_db()
        assert doc.status == 'OBSOLETE'

    def test_engineer_cannot_change_status_to_obsolete(self, auth_client_engineer):
        doc = DocumentFactory.create(status='ACTIVE')
        url = f'/api/v1/edms/documents/{doc.pk}/change-status/'
        r = auth_client_engineer.post(url, {'status': 'OBSOLETE'}, format='json')
        assert r.status_code in (403, 400)


@pytest.mark.django_db
class TestRevision:
    def test_create_revision(self, auth_client_engineer):
        doc = DocumentFactory.create()
        url = '/api/v1/edms/revisions/'
        payload = {
            'document': doc.pk,
            'revision_number': 'R01',
            'status': 'DRAFT',
            'change_description': 'Initial revision for test',
        }
        r = auth_client_engineer.post(url, payload, format='json')
        assert r.status_code == 201
        assert r.data['revision_number'] == 'R01'
