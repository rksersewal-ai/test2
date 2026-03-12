"""Tests for apps.ocr: queue, result, entity."""
import pytest
from unittest.mock import patch, MagicMock
from apps.ocr.models import OCRQueue, OCRResult
from apps.ocr.services import OCRService


@pytest.mark.django_db
class TestOCRQueueAPI:
    def test_list_ocr_queue(self, auth_client_engineer):
        resp = auth_client_engineer.get('/api/v1/ocr/queue/')
        assert resp.status_code == 200

    def test_ocr_stats_endpoint(self, auth_client_engineer):
        resp = auth_client_engineer.get('/api/v1/ocr/queue/stats/')
        assert resp.status_code == 200
        assert 'pending' in resp.data
        assert 'completed' in resp.data

    def test_ocr_results_list(self, auth_client_engineer):
        resp = auth_client_engineer.get('/api/v1/ocr/results/')
        assert resp.status_code == 200


@pytest.mark.django_db
class TestOCRQueueModel:
    def test_retry_failed_raises_for_non_failed(self, db, section, admin_user):
        from apps.edms.models import Category, DocumentType, Document, Revision, FileAttachment
        cat = Category.objects.create(code='TST', name='Test Cat')
        doc = Document.objects.create(document_number='OCR/TEST/001', title='OCR Test Doc',
                                       section=section, category=cat, created_by=admin_user)
        rev = Revision.objects.create(document=doc, revision_number='A', created_by=admin_user)
        fa = FileAttachment.objects.create(
            revision=rev, file_name='test.pdf', file_path='documents/test.pdf',
            file_type='PDF', uploaded_by=admin_user
        )
        queue = OCRQueue.objects.create(file=fa, status=OCRQueue.Status.PENDING)
        with pytest.raises(ValueError):
            OCRService.retry_failed_item(queue.id)
