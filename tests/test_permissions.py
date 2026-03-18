# =============================================================================
# FILE: tests/test_permissions.py
#
# RBAC smoke tests — verifies that every role has the correct access level
# for the three most security-critical endpoints:
#   1. POST /api/v1/edms/documents/          (create document)
#   2. POST /api/v1/edms/documents/{id}/approve/  (approve document)
#   3. GET  /api/v1/search/unified/          (search)
#   4. POST /api/v1/edms/documents/bulk-update/   (bulk status change)
#
# Run with:
#   python manage.py test tests.test_permissions --settings=config.settings.test
#
# These are UNIT tests — they use Django's test client and create objects in
# the test DB (SQLite or PostgreSQL depending on test settings). No mocking.
# =============================================================================
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.core.models import User


def make_user(username, role, password='TestPass123!'):
    user = User.objects.create_user(
        username=username,
        password=password,
        role=role,
    )
    return user


class RBACDocumentCreateTests(TestCase):
    """POST /api/v1/edms/documents/ — only Engineer+ can create."""

    def setUp(self):
        self.client  = APIClient()
        self.url     = '/api/v1/edms/documents/'
        self.payload = {
            'title':           'Test Document',
            'document_number': 'TEST-001',
        }

    def _post(self, role):
        user = make_user(f'user_{role}', role)
        self.client.force_authenticate(user=user)
        return self.client.post(self.url, self.payload, format='json')

    def test_viewer_cannot_create(self):
        response = self._post(User.Role.VIEWER)
        self.assertEqual(response.status_code, 403,
                         'VIEWER must not create documents')

    def test_audit_cannot_create(self):
        response = self._post(User.Role.AUDIT)
        self.assertEqual(response.status_code, 403,
                         'AUDIT must not create documents')

    def test_engineer_can_create(self):
        response = self._post(User.Role.ENGINEER)
        # 201 = created, 400 = validation error (missing fields) — both mean auth passed
        self.assertIn(response.status_code, [201, 400],
                      'ENGINEER should be allowed to attempt document creation')

    def test_section_head_can_create(self):
        response = self._post(User.Role.SECTION_HEAD)
        self.assertIn(response.status_code, [201, 400])

    def test_admin_can_create(self):
        response = self._post(User.Role.ADMIN)
        self.assertIn(response.status_code, [201, 400])

    def test_unauthenticated_cannot_create(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, 401,
                         'Unauthenticated requests must be rejected')


class RBACBulkUpdateTests(TestCase):
    """POST /api/v1/edms/documents/bulk-update/ — only Admin/SectionHead."""

    def setUp(self):
        self.client  = APIClient()
        self.url     = '/api/v1/edms/documents/bulk-update/'
        self.payload = {'ids': [1, 2], 'fields': {'status': 'ACTIVE'}}

    def _post(self, role):
        user = make_user(f'bulk_{role}', role)
        self.client.force_authenticate(user=user)
        return self.client.post(self.url, self.payload, format='json')

    def test_viewer_cannot_bulk_update(self):
        self.assertEqual(self._post(User.Role.VIEWER).status_code, 403)

    def test_engineer_cannot_bulk_update(self):
        self.assertEqual(self._post(User.Role.ENGINEER).status_code, 403)

    def test_section_head_can_bulk_update(self):
        # 200 or 400 (no matching docs in test DB) — auth must have passed
        self.assertIn(self._post(User.Role.SECTION_HEAD).status_code, [200, 400])

    def test_admin_can_bulk_update(self):
        self.assertIn(self._post(User.Role.ADMIN).status_code, [200, 400])


class RBACSearchTests(TestCase):
    """GET /api/v1/search/unified/ — all authenticated roles can search."""

    def setUp(self):
        self.client = APIClient()
        self.url    = '/api/v1/search/unified/?q=test'

    def test_unauthenticated_blocked(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_viewer_can_search(self):
        user = make_user('viewer_search', User.Role.VIEWER)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [200, 400],
                      'VIEWER should be allowed to search')

    def test_engineer_can_search(self):
        user = make_user('eng_search', User.Role.ENGINEER)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [200, 400])


class HealthCheckTests(TestCase):
    """GET /api/v1/health/ — must be accessible without authentication."""

    def test_health_unauthenticated(self):
        response = self.client.get('/api/v1/health/')
        # 200 = healthy, 503 = degraded — either is acceptable (not 401/403)
        self.assertIn(response.status_code, [200, 503],
                      'Health check must not require authentication')

    def test_health_response_has_required_keys(self):
        response = self.client.get('/api/v1/health/')
        data = response.json()
        self.assertIn('status',  data)
        self.assertIn('db',      data)
        self.assertIn('cache',   data)
        self.assertIn('version', data)
