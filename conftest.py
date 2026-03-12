"""Global pytest fixtures for PLW EDMS + LDO."""
import pytest
from rest_framework.test import APIClient
from apps.core.models import User, Section


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def section(db):
    return Section.objects.create(code='TEST', name='Test Section')


@pytest.fixture
def admin_user(db, section):
    return User.objects.create_superuser(
        username='test_admin',
        password='TestAdmin@123',
        full_name='Test Admin',
        role=User.Role.ADMIN,
        section=section,
    )


@pytest.fixture
def engineer_user(db, section):
    return User.objects.create_user(
        username='test_engineer',
        password='TestEngineer@123',
        full_name='Test Engineer',
        role=User.Role.ENGINEER,
        section=section,
    )


@pytest.fixture
def ldo_user(db, section):
    return User.objects.create_user(
        username='test_ldo',
        password='TestLdo@123',
        full_name='Test LDO Staff',
        role=User.Role.LDO_STAFF,
        section=section,
    )


@pytest.fixture
def viewer_user(db, section):
    return User.objects.create_user(
        username='test_viewer',
        password='TestViewer@123',
        full_name='Test Viewer',
        role=User.Role.VIEWER,
        section=section,
    )


@pytest.fixture
def audit_user(db, section):
    return User.objects.create_user(
        username='test_audit',
        password='TestAudit@123',
        full_name='Test Auditor',
        role=User.Role.AUDIT,
        section=section,
    )


@pytest.fixture
def auth_client_admin(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def auth_client_engineer(api_client, engineer_user):
    api_client.force_authenticate(user=engineer_user)
    return api_client


@pytest.fixture
def auth_client_viewer(api_client, viewer_user):
    api_client.force_authenticate(user=viewer_user)
    return api_client


@pytest.fixture
def auth_client_audit(api_client, audit_user):
    api_client.force_authenticate(user=audit_user)
    return api_client
