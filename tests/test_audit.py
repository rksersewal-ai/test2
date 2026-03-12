"""Audit log tests — PRD Section 20."""
import pytest
from apps.audit.models import AuditLog
from apps.audit.services import AuditService
from tests.factories import AuditLogFactory, UserFactory


@pytest.mark.django_db
class TestAuditService:
    def test_creates_log_entry(self, db):
        user = UserFactory.create()
        entry = AuditService.log(
            user=user,
            module=AuditLog.Module.EDMS,
            action='DOCUMENT_CREATE',
            entity_type='Document',
            entity_id=42,
            entity_identifier='PLW/TEST/2026/0001',
            description='Created test document',
        )
        assert entry is not None
        assert entry.pk is not None
        assert entry.username == user.username
        assert entry.action == 'DOCUMENT_CREATE'

    def test_log_is_immutable_via_save(self, db):
        entry = AuditLogFactory.create()
        with pytest.raises(ValueError, match='immutable'):
            entry.action = 'TAMPERED'
            entry.save()

    def test_log_cannot_be_deleted(self, db):
        entry = AuditLogFactory.create()
        with pytest.raises(ValueError, match='cannot be deleted'):
            entry.delete()

    def test_log_never_raises_on_bad_input(self, db):
        # AuditService.log should absorb errors gracefully
        result = AuditService.log(
            user=None,
            module='INVALID_MODULE',  # bad value
            action='TEST',
        )
        # Returns None on error, never raises
        assert result is None or isinstance(result, AuditLog)


@pytest.mark.django_db
class TestAuditLogAPI:
    url = '/api/v1/audit/logs/'

    def test_audit_role_can_list(self, auth_client_audit):
        AuditLogFactory.create_batch(3)
        r = auth_client_audit.get(self.url)
        assert r.status_code == 200
        assert r.data['count'] >= 3

    def test_engineer_cannot_access(self, auth_client_engineer):
        r = auth_client_engineer.get(self.url)
        assert r.status_code == 403

    def test_admin_can_access(self, auth_client_admin):
        r = auth_client_admin.get(self.url)
        assert r.status_code == 200

    def test_audit_log_is_read_only_via_api(self, auth_client_audit):
        # POST should not be allowed (ReadOnlyModelViewSet)
        r = auth_client_audit.post(self.url, {}, format='json')
        assert r.status_code == 405

    def test_filter_by_module(self, auth_client_audit):
        AuditLogFactory.create(module=AuditLog.Module.EDMS)
        AuditLogFactory.create(module=AuditLog.Module.OCR)
        r = auth_client_audit.get(self.url, {'module': 'EDMS'})
        assert r.status_code == 200
        for item in r.data['results']:
            assert item['module'] == 'EDMS'
