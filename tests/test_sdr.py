"""SDR register API regression tests."""

import pytest

from apps.pl_master.models import DrawingMaster, SpecificationMaster
from apps.sdr.models import SDRItem, SDRRecord


BASE = '/api/v1/sdr/'


@pytest.mark.django_db
class TestSDRApi:
    def _create_drawing(self):
        return DrawingMaster.objects.create(
            drawing_number='PLW-DRG-0001',
            drawing_title='Traction Motor General Arrangement',
            current_alteration='A',
        )

    def _create_specification(self):
        return SpecificationMaster.objects.create(
            spec_number='PLW-SPEC-0001',
            spec_title='Traction Motor Test Specification',
            current_alteration='B',
        )

    def _create_record(self, user):
        drawing = self._create_drawing()
        record = SDRRecord.objects.create(
            issue_date='2026-03-18',
            shop_name='AC Machine Shop',
            requesting_official='Requester',
            issuing_official='Issuer',
            receiving_official='Receiver',
            remarks='Issued for production verification.',
            created_by=user,
        )
        SDRItem.objects.create(
            sdr_record=record,
            document_type='DRAWING',
            drawing=drawing,
            document_number='',
            document_title='',
            alteration_no='',
            size='A1',
            copies=2,
            controlled_copy=True,
        )
        return record

    def test_list_returns_paginated_payload(self, auth_client_engineer, engineer_user):
        record = self._create_record(engineer_user)

        response = auth_client_engineer.get(BASE, {'page': 1, 'page_size': 20})

        assert response.status_code == 200
        assert 'results' in response.data
        assert 'count' in response.data
        assert any(item['id'] == record.id for item in response.data['results'])

    def test_search_endpoint_returns_matching_drawings_and_specs(self, auth_client_engineer):
        drawing = self._create_drawing()
        specification = self._create_specification()

        response = auth_client_engineer.get(BASE + 'search/', {'q': 'PLW-', 'type': ''})

        assert response.status_code == 200
        assert any(item['type'] == 'DRAWING' and item['number'] == drawing.drawing_number for item in response.data)
        assert any(item['type'] == 'SPEC' and item['number'] == specification.spec_number for item in response.data)
