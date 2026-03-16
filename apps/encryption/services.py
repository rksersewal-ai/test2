# =============================================================================
# FILE: apps/encryption/services.py
# FR-012: AES-256-CBC encryption at rest for stored document files
# Uses cryptography library. Key stored in settings.EDMS_ENCRYPTION_KEY (env var).
# Also handles TLS enforcement check utility.
# =============================================================================
import os
import base64
import hashlib
from io import BytesIO
from django.conf import settings


class EncryptionService:

    BLOCK_SIZE = 16  # AES block size in bytes

    @staticmethod
    def _get_key() -> bytes:
        """Derive 32-byte AES key from settings.EDMS_ENCRYPTION_KEY."""
        raw = getattr(settings, 'EDMS_ENCRYPTION_KEY', '')
        if not raw:
            raise ValueError(
                'EDMS_ENCRYPTION_KEY not set in settings. '
                'Add to .env: EDMS_ENCRYPTION_KEY=<32-char-secret>'
            )
        return hashlib.sha256(raw.encode()).digest()

    @staticmethod
    def encrypt_file(file_obj) -> tuple[bytes, bytes]:
        """
        Encrypt file using AES-256-CBC.
        Returns (encrypted_bytes, iv) where iv is 16 random bytes.
        """
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.primitives import padding as sym_padding
            from cryptography.hazmat.backends import default_backend
        except ImportError:
            raise RuntimeError('cryptography library required. pip install cryptography')

        key  = EncryptionService._get_key()
        iv   = os.urandom(EncryptionService.BLOCK_SIZE)
        data = file_obj.read() if hasattr(file_obj, 'read') else file_obj

        padder    = sym_padding.PKCS7(128).padder()
        padded    = padder.update(data) + padder.finalize()
        cipher    = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()
        return encrypted, iv

    @staticmethod
    def decrypt_file(encrypted_bytes: bytes, iv: bytes) -> bytes:
        """
        Decrypt AES-256-CBC encrypted bytes using stored IV.
        Returns original plaintext bytes.
        """
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.primitives import padding as sym_padding
            from cryptography.hazmat.backends import default_backend
        except ImportError:
            raise RuntimeError('cryptography library required.')

        key       = EncryptionService._get_key()
        cipher    = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded    = decryptor.update(encrypted_bytes) + decryptor.finalize()
        unpadder  = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(padded) + unpadder.finalize()

    @staticmethod
    def encrypt_to_base64(file_obj) -> dict:
        """
        Encrypt file and return base64-encoded dict suitable for DB storage.
        Returns: {'data': '<b64>', 'iv': '<b64>'}
        """
        encrypted, iv = EncryptionService.encrypt_file(file_obj)
        return {
            'data': base64.b64encode(encrypted).decode(),
            'iv':   base64.b64encode(iv).decode(),
        }

    @staticmethod
    def decrypt_from_base64(data_b64: str, iv_b64: str) -> BytesIO:
        """Decrypt from base64-encoded stored data. Returns BytesIO stream."""
        encrypted = base64.b64decode(data_b64)
        iv        = base64.b64decode(iv_b64)
        plain     = EncryptionService.decrypt_file(encrypted, iv)
        return BytesIO(plain)


class TLSEnforcer:
    """Utility: verify TLS is enforced in Django settings."""

    @staticmethod
    def check_settings() -> dict:
        issues = []
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            issues.append('SECURE_SSL_REDIRECT must be True in production')
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            issues.append('SESSION_COOKIE_SECURE must be True')
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
            issues.append('CSRF_COOKIE_SECURE must be True')
        hsts = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
        if hsts < 31536000:
            issues.append('SECURE_HSTS_SECONDS should be >= 31536000 (1 year)')
        return {
            'tls_compliant': len(issues) == 0,
            'issues': issues,
        }
