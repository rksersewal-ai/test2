# =============================================================================
# FILE: apps/dsign/services.py
# FR-008: Digital Signature business logic
# Sign document, verify signature, revoke signature.
# Uses cryptography library (RSA-2048 + SHA-256, PKCS#1v15 padding).
# IT Act 2000 Section 3 compliant.
# =============================================================================
import hashlib
from django.db import transaction
from django.utils import timezone
from .models import SigningCertificate, DocumentSignature
from apps.edms.models import Document
from apps.versioning.models import DocumentVersion


class DigitalSignatureService:

    @staticmethod
    def _compute_file_checksum(file_obj) -> str:
        hasher = hashlib.sha256()
        if hasattr(file_obj, 'chunks'):
            for chunk in file_obj.chunks():
                hasher.update(chunk)
        else:
            hasher.update(file_obj.read())
        return hasher.hexdigest()

    @staticmethod
    def _rsa_sign(private_key_pem: str, data: bytes) -> str:
        """Sign data using RSA private key, return hex-encoded signature."""
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode(), password=None
            )
            signature = private_key.sign(
                data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return signature.hex()
        except ImportError:
            raise RuntimeError(
                'cryptography library required. Install: pip install cryptography'
            )

    @staticmethod
    def _rsa_verify(public_key_pem: str, data: bytes, signature_hex: str) -> bool:
        """Verify RSA-SHA256 signature against data using public key."""
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.exceptions import InvalidSignature
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            sig_bytes   = bytes.fromhex(signature_hex)
            try:
                public_key.verify(sig_bytes, data, padding.PKCS1v15(), hashes.SHA256())
                return True
            except InvalidSignature:
                return False
        except ImportError:
            raise RuntimeError('cryptography library required.')

    @staticmethod
    @transaction.atomic
    def sign_document(
        document: Document,
        user,
        private_key_pem: str,
        role: str = DocumentSignature.SignatureRole.APPROVED,
        version: DocumentVersion = None,
        remarks: str = '',
    ) -> DocumentSignature:
        """Sign a document. Raises if user has no active certificate."""
        try:
            cert = SigningCertificate.objects.get(
                user=user,
                status=SigningCertificate.CertStatus.ACTIVE
            )
        except SigningCertificate.DoesNotExist:
            raise ValueError(
                f'No active signing certificate found for user {user.username}. '
                'Please register a PKI certificate first.'
            )

        if timezone.now() > cert.valid_until:
            cert.status = SigningCertificate.CertStatus.EXPIRED
            cert.save(update_fields=['status'])
            raise ValueError('Signing certificate has expired.')

        # Build signing payload: doc_number + version + timestamp
        payload = (
            f"{document.document_number}|"
            f"{version.version_number if version else 'HEAD'}|"
            f"{timezone.now().isoformat()}"
        ).encode()

        file_checksum = (
            version.checksum_sha256 if version else document.document_number
        )
        signature_hash = DigitalSignatureService._rsa_sign(private_key_pem, payload)

        sig = DocumentSignature.objects.create(
            document=document,
            version=version,
            signed_by=user,
            certificate=cert,
            role=role,
            signature_hash=signature_hash,
            file_checksum=file_checksum,
            status=DocumentSignature.SignatureStatus.VALID,
            remarks=remarks,
            it_act_compliant=True,
        )
        return sig

    @staticmethod
    def verify_signature(signature: DocumentSignature) -> bool:
        """Re-verify a stored signature against the certificate public key."""
        if not signature.certificate:
            return False
        payload = (
            f"{signature.document.document_number}|"
            f"{signature.version.version_number if signature.version else 'HEAD'}|"
        ).encode()
        result = DigitalSignatureService._rsa_verify(
            signature.certificate.public_key_pem,
            payload,
            signature.signature_hash
        )
        if not result:
            signature.status = DocumentSignature.SignatureStatus.INVALID
            signature.save(update_fields=['status'])
        return result

    @staticmethod
    def revoke(signature: DocumentSignature, reason: str = ''):
        """Revoke a digital signature."""
        signature.status  = DocumentSignature.SignatureStatus.REVOKED
        signature.remarks = f'REVOKED: {reason}' if reason else 'REVOKED'
        signature.save(update_fields=['status', 'remarks'])
