# =============================================================================
# FILE: tests/test_rbac.py
# FR-009: Tests for RBAC module
# Covers role assignment, permission checking, object-level overrides,
# role scoping, and 8-role model completeness.
# =============================================================================
import pytest
from apps.rbac.models import UserRole, DocumentPermissionOverride, Role, Permission, ROLE_PERMISSIONS
from apps.rbac.services import RBACService
from tests.factories import UserFactory, DocumentFactory


@pytest.mark.django_db
class TestRoleAssignment:

    def test_assign_role(self):
        user   = UserFactory()
        granter = UserFactory()
        ur = RBACService.assign_role(user, Role.DEALING_CLERK, granter=granter)
        assert ur.pk is not None
        assert ur.role == Role.DEALING_CLERK
        assert ur.is_active is True

    def test_revoke_role(self):
        user = UserFactory()
        RBACService.assign_role(user, Role.REVIEWER)
        RBACService.revoke_role(user, Role.REVIEWER)
        roles = RBACService.get_active_roles(user)
        assert Role.REVIEWER not in roles

    def test_all_8_roles_defined(self):
        expected = {
            Role.SYSTEM_ADMIN, Role.DMS_ADMIN, Role.SECTION_OFFICER,
            Role.DEALING_CLERK, Role.DRAWING_OFFICER, Role.REVIEWER,
            Role.VIEWER, Role.AUDITOR
        }
        actual = {r for r, _ in Role.choices}
        assert expected == actual


@pytest.mark.django_db
class TestPermissionChecking:

    def test_system_admin_has_all_perms(self):
        user = UserFactory()
        RBACService.assign_role(user, Role.SYSTEM_ADMIN)
        all_perms = [p for p, _ in Permission.choices]
        for perm in all_perms:
            assert RBACService.has_permission(user, perm), f'SYSTEM_ADMIN missing: {perm}'

    def test_viewer_cannot_create(self):
        user = UserFactory()
        RBACService.assign_role(user, Role.VIEWER)
        assert not RBACService.has_permission(user, Permission.DOC_CREATE)

    def test_viewer_can_read(self):
        user = UserFactory()
        RBACService.assign_role(user, Role.VIEWER)
        assert RBACService.has_permission(user, Permission.DOC_READ)

    def test_auditor_can_read_audit(self):
        user = UserFactory()
        RBACService.assign_role(user, Role.AUDITOR)
        assert RBACService.has_permission(user, Permission.AUDIT_READ)

    def test_auditor_cannot_approve(self):
        user = UserFactory()
        RBACService.assign_role(user, Role.AUDITOR)
        assert not RBACService.has_permission(user, Permission.DOC_APPROVE)

    def test_section_officer_can_approve(self):
        user = UserFactory()
        RBACService.assign_role(user, Role.SECTION_OFFICER)
        assert RBACService.has_permission(user, Permission.DOC_APPROVE)

    def test_dealing_clerk_cannot_approve(self):
        user = UserFactory()
        RBACService.assign_role(user, Role.DEALING_CLERK)
        assert not RBACService.has_permission(user, Permission.DOC_APPROVE)


@pytest.mark.django_db
class TestObjectLevelOverrides:

    def test_deny_override_blocks_viewer(self):
        user = UserFactory()
        doc  = DocumentFactory()
        RBACService.assign_role(user, Role.VIEWER)
        DocumentPermissionOverride.objects.create(
            user=user, document=doc,
            permission=Permission.DOC_READ,
            override=DocumentPermissionOverride.OverrideType.DENY,
            reason='Confidential document',
        )
        assert not RBACService.has_permission(user, Permission.DOC_READ, document=doc)

    def test_grant_override_allows_viewer_to_approve(self):
        user = UserFactory()
        doc  = DocumentFactory()
        RBACService.assign_role(user, Role.VIEWER)
        DocumentPermissionOverride.objects.create(
            user=user, document=doc,
            permission=Permission.DOC_APPROVE,
            override=DocumentPermissionOverride.OverrideType.GRANT,
            reason='Special delegation',
        )
        assert RBACService.has_permission(user, Permission.DOC_APPROVE, document=doc)

    def test_no_role_user_denied(self):
        user = UserFactory()
        assert not RBACService.has_permission(user, Permission.DOC_READ)
