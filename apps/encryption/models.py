# =============================================================================
# FILE: apps/encryption/models.py
# FR-012: Stores encrypted file blobs with IV for AES-256-CBC at-rest encryption.
# FileAttachment can optionally reference an EncryptedBlob for secure storage.
# =============================================================================
from django.db import models
from apps.edms.models import FileAttachment


class EncryptedBlob(models.Model):
    """Stores AES-256-CBC encrypted file data alongside its IV."""

    attachment      = models.OneToOneField(
        FileAttachment, on_delete=models.CASCADE,
        related_name='encrypted_blob'
    )
    encrypted_data  = models.BinaryField(help_text='AES-256-CBC encrypted file bytes')
    iv              = models.BinaryField(max_length=16, help_text='16-byte AES IV')
    key_hint        = models.CharField(
        max_length=50, blank=True,
        help_text='Identifier for which key was used (for key rotation support)'
    )
    encrypted_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'enc_encrypted_blob'

    def __str__(self):
        return f"EncryptedBlob for {self.attachment.file_name}"
