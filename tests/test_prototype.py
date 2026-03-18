"""Prototype inspection API regression tests."""

import pytest

from prototype.models import Inspection, PunchItem


BASE = '/api/v1/prototype/'


@pytest.mark.django_db
class TestPrototypeApi:
    def _create_inspection(self, user):
        inspection = Inspection.objects.create(
            loco_number='31001',
            loco_class='WAG-9',
            inspection_type='Prototype',
            inspection_date='2026-03-18',
            inspector='Inspector Singh',
            status='Open',
            remarks='Initial prototype run.',
            created_by=user,
        )
        PunchItem.objects.create(
            inspection=inspection,
            description='Loose terminal connection',
            status='Open',
            raised_by='Inspector Singh',
        )
        return inspection

    def test_list_returns_paginated_payload_with_open_punch_count(self, auth_client_engineer, engineer_user):
        inspection = self._create_inspection(engineer_user)

        response = auth_client_engineer.get(BASE + 'inspections/', {'page': 1, 'page_size': 20, 'status': 'Open'})

        assert response.status_code == 200
        assert 'results' in response.data
        assert any(item['id'] == inspection.id and item['open_punch_count'] == 1 for item in response.data['results'])

    def test_close_actions_set_closed_status_values(self, auth_client_engineer, engineer_user):
        inspection = self._create_inspection(engineer_user)
        punch_item = inspection.punch_items.get()

        close_punch = auth_client_engineer.post(
            BASE + f'punch-items/{punch_item.id}/close/',
            {'remarks': 'Rectified during inspection.'},
            format='json',
        )
        inspection_close = auth_client_engineer.post(BASE + f'inspections/{inspection.id}/close/')

        punch_item.refresh_from_db()
        inspection.refresh_from_db()

        assert close_punch.status_code == 200
        assert inspection_close.status_code == 200
        assert punch_item.status == 'Closed'
        assert inspection.status == 'Closed'
