"""Tests for apps.audit: AuditLog immutability, access log."""
import pytest
from apps.audit.models import AuditLog, DocumentAccessLog


@pytest.mark.django_db
class TestAuditLogImmutability:
    def test_audit_log_insert(self, admin_user):
        log = AuditLog.objects.create(
            user=admin_user,
            username=admin_user.username,
            action='CREATE',
            module='edms',
            entity_type='Document',
            entity_id='1',
            entity_identifier='SPEC/TEST/001',
            description='Created document',
            success=True,
        )
        assert log.pk is not None

    def test_audit_log_update_raises(self, admin_user):
        log = AuditLog.objects.create(
            user=admin_user, username=admin_user.username,
            action='VIEW', module='edms', entity_type='Document',
            entity_id='1', entity_identifier='DOC/001',
        )
        with pytest.raises(PermissionError):
            log.action = 'MODIFIED'
            log.save()

    def test_audit_log_delete_raises(self, admin_user):
        log = AuditLog.objects.create(
            user=admin_user, username=admin_user.username,
            action='VIEW', module='edms', entity_type='Document',
            entity_id='2', entity_identifier='DOC/002',
        )
        with pytest.raises(PermissionError):
            log.delete()

    def test_audit_log_api_requires_audit_role(self, auth_client_engineer):
        resp = auth_client_engineer.get('/api/v1/audit/logs/')
        assert resp.status_code == 403

    def test_audit_log_api_accessible_by_audit(self, auth_client_audit):
        resp = auth_client_audit.get('/api/v1/audit/logs/')
        assert resp.status_code == 200
