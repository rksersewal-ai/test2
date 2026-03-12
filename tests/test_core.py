"""Tests for apps.core: User, Section, RBAC."""
import pytest
from django.urls import reverse
from apps.core.models import User, Section


@pytest.mark.django_db
class TestSectionAPI:
    def test_list_sections_authenticated(self, auth_client_engineer):
        Section.objects.create(code='MECH', name='Mechanical')
        resp = auth_client_engineer.get('/api/v1/core/sections/')
        assert resp.status_code == 200

    def test_list_sections_unauthenticated(self, api_client):
        resp = api_client.get('/api/v1/core/sections/')
        assert resp.status_code == 401

    def test_create_section_admin_only(self, auth_client_admin, auth_client_engineer):
        data = {'code': 'ELEC', 'name': 'Electrical', 'description': '', 'is_active': True}
        resp = auth_client_admin.post('/api/v1/core/sections/', data)
        assert resp.status_code == 201
        resp2 = auth_client_engineer.post('/api/v1/core/sections/', data)
        assert resp2.status_code == 403


@pytest.mark.django_db
class TestUserAPI:
    def test_current_user_me(self, auth_client_engineer, engineer_user):
        resp = auth_client_engineer.get('/api/v1/core/me/')
        assert resp.status_code == 200
        assert resp.data['username'] == engineer_user.username
        assert resp.data['role'] == User.Role.ENGINEER

    def test_list_users_admin_only(self, auth_client_admin, auth_client_viewer):
        resp = auth_client_admin.get('/api/v1/core/users/')
        assert resp.status_code == 200
        resp2 = auth_client_viewer.get('/api/v1/core/users/')
        assert resp2.status_code == 403

    def test_create_user_by_admin(self, auth_client_admin, section):
        data = {
            'username': 'new_eng',
            'password': 'NewEng@2026!!',
            'full_name': 'New Engineer',
            'employee_code': 'EMP999',
            'role': User.Role.ENGINEER,
            'section': section.id,
        }
        resp = auth_client_admin.post('/api/v1/core/users/', data)
        assert resp.status_code == 201
        assert User.objects.filter(username='new_eng').exists()


@pytest.mark.django_db
class TestRBACPermissions:
    def test_viewer_cannot_create_document(self, auth_client_viewer):
        resp = auth_client_viewer.post('/api/v1/edms/documents/', {})
        assert resp.status_code == 403

    def test_viewer_cannot_access_audit_log(self, auth_client_viewer):
        resp = auth_client_viewer.get('/api/v1/audit/logs/')
        assert resp.status_code == 403

    def test_audit_can_read_logs(self, auth_client_audit):
        resp = auth_client_audit.get('/api/v1/audit/logs/')
        assert resp.status_code == 200
