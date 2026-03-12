"""Tests for apps.edms: Document, Revision, FileAttachment."""
import pytest
from apps.edms.models import Document, Revision, Category, DocumentType
from apps.core.models import Section


@pytest.fixture
def category(db):
    return Category.objects.create(code='SPEC', name='Specifications')


@pytest.fixture
def doc_type(db):
    return DocumentType.objects.create(code='RDSO', name='RDSO Spec')


@pytest.fixture
def document(db, section, category, doc_type, admin_user):
    return Document.objects.create(
        document_number='SPEC/WAG9/001',
        title='WAG9 Traction Motor Spec',
        category=category,
        document_type=doc_type,
        section=section,
        status=Document.Status.ACTIVE,
        source_standard='RDSO',
        created_by=admin_user,
    )


@pytest.mark.django_db
class TestDocumentModel:
    def test_document_str(self, document):
        assert 'SPEC/WAG9/001' in str(document)

    def test_document_unique_number(self, db, section, category, admin_user):
        Document.objects.create(
            document_number='UNIQUE/001', title='Doc 1',
            section=section, category=category, created_by=admin_user
        )
        with pytest.raises(Exception):
            Document.objects.create(
                document_number='UNIQUE/001', title='Doc Duplicate',
                section=section, created_by=admin_user
            )

    def test_revision_unique_per_document(self, db, document, admin_user):
        Revision.objects.create(
            document=document, revision_number='A', status=Revision.Status.CURRENT, created_by=admin_user
        )
        with pytest.raises(Exception):
            Revision.objects.create(
                document=document, revision_number='A', status=Revision.Status.CURRENT, created_by=admin_user
            )


@pytest.mark.django_db
class TestDocumentAPI:
    def test_list_documents(self, auth_client_engineer):
        resp = auth_client_engineer.get('/api/v1/edms/documents/')
        assert resp.status_code == 200
        assert 'results' in resp.data

    def test_create_document_engineer(self, auth_client_engineer, section, category, doc_type):
        data = {
            'document_number': 'TEST/DRG/001',
            'title': 'Test Drawing',
            'status': 'ACTIVE',
            'source_standard': 'RDSO',
            'section': section.id,
            'category': category.id,
            'document_type': doc_type.id,
            'description': '',
            'eoffice_file_number': '',
            'eoffice_subject': '',
            'keywords': 'WAG9, traction',
        }
        resp = auth_client_engineer.post('/api/v1/edms/documents/', data)
        assert resp.status_code == 201
        assert Document.objects.filter(document_number='TEST/DRG/001').exists()

    def test_viewer_cannot_create_document(self, auth_client_viewer, section, category):
        data = {'document_number': 'TEST/DRG/002', 'title': 'Test'}
        resp = auth_client_viewer.post('/api/v1/edms/documents/', data)
        assert resp.status_code == 403

    def test_document_search(self, auth_client_engineer, document):
        resp = auth_client_engineer.get('/api/v1/edms/documents/?search=WAG9')
        assert resp.status_code == 200

    def test_document_filter_by_status(self, auth_client_engineer, document):
        resp = auth_client_engineer.get('/api/v1/edms/documents/?status=ACTIVE')
        assert resp.status_code == 200
        for item in resp.data.get('results', []):
            assert item['status'] == 'ACTIVE'
