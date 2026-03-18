"""PL master API regression tests."""

import pytest


BASE = '/api/v1/pl-master/'


@pytest.mark.django_db
class TestPLMasterApi:
    def test_create_rejects_safety_item_without_classification(self, auth_client_engineer):
        response = auth_client_engineer.post(
            BASE,
            {
                'pl_number': 'PLW-PL-0001',
                'part_description': 'Safety critical traction bracket',
                'inspection_category': 'CAT-A',
                'safety_item': True,
            },
            format='json',
        )

        assert response.status_code == 400
        assert 'safety_classification' in response.data

    def test_create_accepts_safety_item_with_classification(self, auth_client_engineer):
        response = auth_client_engineer.post(
            BASE,
            {
                'pl_number': 'PLW-PL-0002',
                'part_description': 'Brake cylinder mounting arrangement',
                'inspection_category': 'CAT-A',
                'safety_item': True,
                'safety_classification': 'HIGH',
                'used_in': ['WAG-9'],
            },
            format='json',
        )

        assert response.status_code == 201
        assert response.data['pl_number'] == 'PLW-PL-0002'
        assert response.data['safety_classification'] == 'HIGH'
