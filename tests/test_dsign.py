# =============================================================================
# FILE: tests/test_dsign.py
# FR-008: Tests for Digital Signature module
# Covers certificate registration, sign, verify, revoke.
# Uses unittest.mock to avoid requiring actual RSA keys in test env.
# =============================================================================
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from apps.dsign.models import SigningCertificate, DocumentSignature
from apps.dsign.services import DigitalSignatureService
from tests.factories import UserFactory, DocumentFactory


@pytest.mark.django_db
class TestSigningCertificate:

    def test_create_certificate(self):
        user = UserFactory()
        cert = SigningCertificate.objects.create(
            user=user,
            certificate_pem='-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----',
            public_key_pem='-----BEGIN PUBLIC KEY-----\nTEST\n-----END PUBLIC KEY-----',
            serial_number='SN-2026-001',
            issued_by='PLW Internal CA',
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=365),
            status=SigningCertificate.CertStatus.ACTIVE,
        )
        assert cert.pk is not None
        assert cert.status == 'ACTIVE'

    def test_expired_cert_raises(self):
        user = UserFactory()
        doc  = DocumentFactory()
        SigningCertificate.objects.create(
            user=user,
            certificate_pem='CERT',
            public_key_pem='KEY',
            serial_number='SN-EXP-001',
            issued_by='CA',
            valid_from=timezone.now() - timedelta(days=400),
            valid_until=timezone.now() - timedelta(days=1),  # already expired
            status=SigningCertificate.CertStatus.ACTIVE,
        )
        with patch.object(DigitalSignatureService, '_rsa_sign', return_value='abc123'):
            with pytest.raises(ValueError, match='expired'):
                DigitalSignatureService.sign_document(
                    doc, user, 'fake_private_key'
                )

    def test_no_cert_raises(self):
        user = UserFactory()
        doc  = DocumentFactory()
        with pytest.raises(ValueError, match='No active signing certificate'):
            DigitalSignatureService.sign_document(doc, user, 'key')


@pytest.mark.django_db
class TestSignAndVerify:

    def _make_active_cert(self, user):
        return SigningCertificate.objects.create(
            user=user,
            certificate_pem='CERT',
            public_key_pem='PUBKEY',
            serial_number=f'SN-{user.pk}',
            issued_by='PLW CA',
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=365),
            status=SigningCertificate.CertStatus.ACTIVE,
        )

    def test_sign_creates_signature_record(self):
        user = UserFactory()
        doc  = DocumentFactory()
        self._make_active_cert(user)
        with patch.object(DigitalSignatureService, '_rsa_sign', return_value='mocked_sig_hex'):
            sig = DigitalSignatureService.sign_document(
                doc, user, 'fake_private_key',
                role=DocumentSignature.SignatureRole.APPROVED
            )
        assert sig.pk is not None
        assert sig.signature_hash == 'mocked_sig_hex'
        assert sig.status == DocumentSignature.SignatureStatus.VALID
        assert sig.it_act_compliant is True
        assert sig.role == 'APPROVED'

    def test_verify_valid_signature(self):
        user = UserFactory()
        doc  = DocumentFactory()
        self._make_active_cert(user)
        with patch.object(DigitalSignatureService, '_rsa_sign', return_value='valid_hex'):
            sig = DigitalSignatureService.sign_document(doc, user, 'key')
        with patch.object(DigitalSignatureService, '_rsa_verify', return_value=True):
            result = DigitalSignatureService.verify_signature(sig)
        assert result is True

    def test_verify_invalid_marks_invalid(self):
        user = UserFactory()
        doc  = DocumentFactory()
        self._make_active_cert(user)
        with patch.object(DigitalSignatureService, '_rsa_sign', return_value='bad_hex'):
            sig = DigitalSignatureService.sign_document(doc, user, 'key')
        with patch.object(DigitalSignatureService, '_rsa_verify', return_value=False):
            result = DigitalSignatureService.verify_signature(sig)
        sig.refresh_from_db()
        assert result is False
        assert sig.status == DocumentSignature.SignatureStatus.INVALID

    def test_revoke_signature(self):
        user = UserFactory()
        doc  = DocumentFactory()
        self._make_active_cert(user)
        with patch.object(DigitalSignatureService, '_rsa_sign', return_value='hex'):
            sig = DigitalSignatureService.sign_document(doc, user, 'key')
        DigitalSignatureService.revoke(sig, reason='Document superseded')
        sig.refresh_from_db()
        assert sig.status == DocumentSignature.SignatureStatus.REVOKED
        assert 'REVOKED' in sig.remarks
