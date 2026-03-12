"""Core app tests — user model, RBAC, JWT auth — PRD Section 4."""
import pytest
from apps.core.models import User
from tests.factories import UserFactory, SectionFactory

TOKEN_URL = '/api/v1/auth/token/'


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self, db):
        u = UserFactory.create()
        assert u.pk is not None
        assert u.is_active

    def test_roles_available(self):
        roles = [r.value for r in User.Role]
        assert 'ADMIN' in roles
        assert 'ENGINEER' in roles
        assert 'VIEWER' in roles
        assert 'AUDIT' in roles

    def test_user_str(self, db):
        u = UserFactory.create(username='rahul', full_name='Rahul Kumar')
        assert 'rahul' in str(u).lower() or 'Rahul' in str(u)


@pytest.mark.django_db
class TestJWTAuth:
    def test_obtain_token_with_valid_creds(self, api_client, db):
        user = UserFactory.create()
        user.set_password('Test@12345')
        user.save()
        r = api_client.post(TOKEN_URL, {
            'username': user.username,
            'password': 'Test@12345',
        }, format='json')
        assert r.status_code == 200
        assert 'access' in r.data
        assert 'refresh' in r.data

    def test_wrong_password_rejected(self, api_client, db):
        user = UserFactory.create()
        r = api_client.post(TOKEN_URL, {
            'username': user.username,
            'password': 'WRONGPASSWORD',
        }, format='json')
        assert r.status_code == 401

    def test_inactive_user_blocked(self, api_client, db):
        user = UserFactory.create(is_active=False)
        user.set_password('Test@12345')
        user.save()
        r = api_client.post(TOKEN_URL, {
            'username': user.username,
            'password': 'Test@12345',
        }, format='json')
        assert r.status_code == 401


@pytest.mark.django_db
class TestRBAC:
    def test_viewer_gets_403_on_post(self, auth_client_viewer, section):
        r = auth_client_viewer.post('/api/v1/edms/documents/', {}, format='json')
        assert r.status_code == 403

    def test_unauthenticated_gets_401(self, api_client):
        r = api_client.get('/api/v1/edms/documents/')
        assert r.status_code == 401

    def test_engineer_can_read(self, auth_client_engineer):
        r = auth_client_engineer.get('/api/v1/edms/documents/')
        assert r.status_code == 200
