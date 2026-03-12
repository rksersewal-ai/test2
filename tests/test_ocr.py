"""OCR queue and entity parser tests — PRD Section 19."""
import pytest
from apps.ocr.pipeline.entity_parser import EntityParser
from tests.factories import OCRQueueFactory, OCRResultFactory, FileAttachmentFactory


class TestEntityParser:
    """Unit tests — no DB needed."""

    def test_extracts_plw_doc_number(self):
        entities = EntityParser.extract('Refer to PLW/SPEC/2024/0023 for details')
        doc_nums = [e for e in entities if e['type'] == 'DOC_NUM']
        assert any('PLW/SPEC/2024/0023' in e['value'] for e in doc_nums)

    def test_extracts_rdso_spec(self):
        entities = EntityParser.extract('As per RDSO/PE/SPEC/TL/0013 Rev-4')
        specs = [e for e in entities if e['type'] == 'SPEC']
        assert len(specs) >= 1

    def test_extracts_is_standard(self):
        entities = EntityParser.extract('Compliance with IS:3043-2019 required')
        stds = [e for e in entities if e['type'] == 'STD']
        assert len(stds) >= 1

    def test_extracts_din_standard(self):
        entities = EntityParser.extract('Per DIN 7168-medium tolerance')
        stds = [e for e in entities if e['type'] == 'STD']
        assert len(stds) >= 1

    def test_extracts_drawing_number(self):
        entities = EntityParser.extract('See drawing ELW/4/3/027 Rev B')
        dwgs = [e for e in entities if e['type'] == 'DWG']
        assert len(dwgs) >= 1

    def test_empty_text_returns_empty_list(self):
        assert EntityParser.extract('') == []
        assert EntityParser.extract('   ') == []

    def test_no_false_positives_on_plain_text(self):
        entities = EntityParser.extract('The quick brown fox jumps over the lazy dog.')
        assert len(entities) == 0


@pytest.mark.django_db
class TestOCRQueue:
    def test_queue_item_created(self, db):
        q = OCRQueueFactory.create()
        assert q.pk is not None
        assert q.status == 'PENDING'

    def test_result_linked_to_queue(self, db):
        result = OCRResultFactory.create()
        assert result.queue_item is not None
        assert result.full_text != ''

    def test_ocr_api_requires_auth(self, api_client):
        r = api_client.get('/api/v1/ocr/queue/')
        assert r.status_code == 401

    def test_engineer_can_list_ocr_queue(self, auth_client_engineer):
        OCRQueueFactory.create_batch(2)
        r = auth_client_engineer.get('/api/v1/ocr/queue/')
        assert r.status_code == 200
