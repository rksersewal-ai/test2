# =============================================================================
# FILE: apps/dsign/models.py
# FR-008: Digital Signatures
# PKI-based digital signatures compliant with IT Act 2000 (India).
# Uses RSA-2048 + SHA-256. Stores certificate, public key, signature hash.
# =============================================================================
from django.db import models
from django.conf import settings
from apps.edms.models import Document
from apps.versioning.models import DocumentVersion


class SigningCertificate(models.Model):
    """Stores user PKI certificate (public key + cert metadata)."""

    class CertStatus(models.TextChoices):
        ACTIVE  = 'ACTIVE',  'Active'
        REVOKED = 'REVOKED', 'Revoked'
        EXPIRED = 'EXPIRED', 'Expired'

    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='signing_certificate'
    )
    certificate_pem = models.TextField(help_text='PEM-encoded X.509 certificate')
    public_key_pem  = models.TextField(help_text='PEM-encoded RSA public key')
    serial_number   = models.CharField(max_length=100, unique=True)
    issued_by       = models.CharField(max_length=300, blank=True,
                                       help_text='CA / Issuing authority')
    valid_from      = models.DateTimeField()
    valid_until     = models.DateTimeField()
    status          = models.CharField(max_length=20, choices=CertStatus.choices,
                                       default=CertStatus.ACTIVE)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dsign_certificate'

    def __str__(self):
        return f"{self.user.username} | {self.serial_number} [{self.status}]"


class DocumentSignature(models.Model):
    """Records a digital signature event on a document version."""

    class SignatureStatus(models.TextChoices):
        VALID    = 'VALID',    'Valid'
        INVALID  = 'INVALID',  'Invalid'
        REVOKED  = 'REVOKED',  'Revoked'

    class SignatureRole(models.TextChoices):
        PREPARED  = 'PREPARED',  'Prepared By'
        REVIEWED  = 'REVIEWED',  'Reviewed By'
        APPROVED  = 'APPROVED',  'Approved By'
        VERIFIED  = 'VERIFIED',  'Verified By'

    document        = models.ForeignKey(Document, on_delete=models.CASCADE,
                                        related_name='signatures')
    version         = models.ForeignKey(DocumentVersion, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='signatures')
    signed_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT,
        related_name='document_signatures'
    )
    certificate     = models.ForeignKey(
        SigningCertificate, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='signatures'
    )
    role            = models.CharField(max_length=20, choices=SignatureRole.choices,
                                       default=SignatureRole.APPROVED)
    signature_hash  = models.CharField(max_length=512,
                                       help_text='RSA-SHA256 signature (hex encoded)')
    file_checksum   = models.CharField(max_length=64,
                                       help_text='SHA-256 of the signed file at signing time')
    status          = models.CharField(max_length=20, choices=SignatureStatus.choices,
                                       default=SignatureStatus.VALID)
    remarks         = models.TextField(blank=True)
    signed_at       = models.DateTimeField(auto_now_add=True)
    it_act_compliant = models.BooleanField(default=True,
                                           help_text='IT Act 2000 Section 3 compliance flag')

    class Meta:
        db_table = 'dsign_signature'
        ordering = ['-signed_at']

    def __str__(self):
        return (
            f"{self.document.document_number} — "
            f"{self.signed_by.username} [{self.role}] @ {self.signed_at:%Y-%m-%d %H:%M}"
        )
