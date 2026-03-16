# =============================================================================
# FILE: tests/test_phase2_integration.py
# Phase 2 Integration Tests — FR-008, FR-009, FR-011, FR-012
# End-to-end: RBAC → Sign → Lifecycle assign → Legal hold → Archive
# Validates PRD Phase 2 success criteria.
# =============================================================================
import pytest
from unittest.mock import patch
from datetime import date
from django.utils import timezone
from datetime import timedelta
from apps.rbac.models import Role, Permission
from apps.rbac.services import RBACService
from apps.dsign.models import SigningCertificate, DocumentSignature
from apps.dsign.services import DigitalSignatureService
from apps.lifecycle.models import RetentionPolicy, DocumentLifecycle
from apps.lifecycle.services import LifecycleService
from tests.factories import UserFactory, DocumentFactory


@pytest.mark.django_db
class TestPhase2EndToEnd:

    def test_full_phase2_flow(self):
        """Full Phase 2 flow: Assign roles → Check permissions → Sign → Lifecycle."""

        # Setup users
        admin          = UserFactory()
        section_officer = UserFactory()
        clerk          = UserFactory()
        auditor        = UserFactory()

        # FR-009: Assign 8 roles
        RBACService.assign_role(admin, Role.SYSTEM_ADMIN)
        RBACService.assign_role(section_officer, Role.SECTION_OFFICER)
        RBACService.assign_role(clerk, Role.DEALING_CLERK)
        RBACService.assign_role(auditor, Role.AUDITOR)

        # FR-009: Verify permissions
        assert RBACService.has_permission(admin, Permission.USER_MANAGE)
        assert RBACService.has_permission(section_officer, Permission.DOC_APPROVE)
        assert not RBACService.has_permission(clerk, Permission.DOC_APPROVE)
        assert RBACService.has_permission(auditor, Permission.AUDIT_READ)
        assert not RBACService.has_permission(auditor, Permission.DOC_DELETE)

        # FR-008: Setup digital signature
        doc = DocumentFactory()
        SigningCertificate.objects.create(
            user=section_officer,
            certificate_pem='CERT', public_key_pem='PUBKEY',
            serial_number='SN-SO-001', issued_by='PLW CA',
            valid_from=timezone.now() - timedelta(hours=1),
            valid_until=timezone.now() + timedelta(days=365),
            status=SigningCertificate.CertStatus.ACTIVE,
        )
        with patch.object(DigitalSignatureService, '_rsa_sign', return_value='sig_hex_so'):
            sig = DigitalSignatureService.sign_document(
                doc, section_officer, 'private_key',
                role=DocumentSignature.SignatureRole.APPROVED
            )
        assert sig.it_act_compliant is True
        assert sig.status == DocumentSignature.SignatureStatus.VALID

        # FR-011: Assign lifecycle policy
        policy = RetentionPolicy.objects.create(
            name='Railways 7yr', retention_years=7,
            action_after_retention='ARCHIVE',
            legal_basis='Railways Act 1989'
        )
        lc = LifecycleService.assign_policy(doc, policy, date(2026, 1, 1), section_officer)
        assert lc.state == DocumentLifecycle.LifecycleState.ACTIVE
        assert lc.retention_due_date == date(2033, 1, 1)

        # FR-011: Auditor places legal hold
        lc = LifecycleService.place_legal_hold(doc, 'CAG audit probe', auditor)
        assert lc.state == DocumentLifecycle.LifecycleState.LEGAL_HOLD

        # FR-011: Release and archive
        lc = LifecycleService.release_legal_hold(doc, admin)
        lc = LifecycleService.archive(doc, admin, 'Document superseded after signing')
        assert lc.state == DocumentLifecycle.LifecycleState.ARCHIVED

    def test_rbac_blocks_unauthorized_operation(self):
        """PRD KPI: Zero unauthorized access events."""
        viewer = UserFactory()
        doc    = DocumentFactory()
        RBACService.assign_role(viewer, Role.VIEWER)
        # Viewer cannot sign or approve
        assert not RBACService.has_permission(viewer, Permission.DOC_SIGN)
        assert not RBACService.has_permission(viewer, Permission.DOC_APPROVE)
        assert not RBACService.has_permission(viewer, Permission.DOC_DELETE)
        # Viewer can read
        assert RBACService.has_permission(viewer, Permission.DOC_READ)
