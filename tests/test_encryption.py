# =============================================================================
# FILE: tests/test_encryption.py
# FR-012: Tests for AES-256 Encryption service
# Covers encrypt/decrypt roundtrip, key derivation, base64 encode/decode,
# missing key error, and TLS settings check.
# =============================================================================
import pytest
from io import BytesIO
from unittest.mock import patch
from django.test import override_settings
from apps.encryption.services import EncryptionService, TLSEnforcer


class TestAES256Encryption:

    @override_settings(EDMS_ENCRYPTION_KEY='testkey_32chars_padded_for_tests!')
    def test_encrypt_decrypt_roundtrip(self):
        plaintext = b'This is a secret PLW document content.'
        file_obj  = BytesIO(plaintext)
        encrypted, iv = EncryptionService.encrypt_file(file_obj)
        assert encrypted != plaintext
        decrypted = EncryptionService.decrypt_file(encrypted, iv)
        assert decrypted == plaintext

    @override_settings(EDMS_ENCRYPTION_KEY='testkey_32chars_padded_for_tests!')
    def test_different_iv_each_time(self):
        file1 = BytesIO(b'same content')
        file2 = BytesIO(b'same content')
        _, iv1 = EncryptionService.encrypt_file(file1)
        _, iv2 = EncryptionService.encrypt_file(file2)
        assert iv1 != iv2  # IVs must be random

    @override_settings(EDMS_ENCRYPTION_KEY='testkey_32chars_padded_for_tests!')
    def test_base64_roundtrip(self):
        import json
        from io import BytesIO
        content  = b'WAG9 locomotive drawing confidential'
        file_obj = BytesIO(content)
        encoded  = EncryptionService.encrypt_to_base64(file_obj)
        assert 'data' in encoded
        assert 'iv' in encoded
        stream = EncryptionService.decrypt_from_base64(encoded['data'], encoded['iv'])
        assert stream.read() == content

    @override_settings(EDMS_ENCRYPTION_KEY='')
    def test_missing_key_raises(self):
        file_obj = BytesIO(b'test')
        with pytest.raises(ValueError, match='EDMS_ENCRYPTION_KEY not set'):
            EncryptionService.encrypt_file(file_obj)

    @override_settings(EDMS_ENCRYPTION_KEY='testkey_32chars_padded_for_tests!')
    def test_tampered_data_raises(self):
        file_obj  = BytesIO(b'original content here that is long enough')
        encrypted, iv = EncryptionService.encrypt_file(file_obj)
        # Tamper with encrypted bytes
        tampered = bytes([b ^ 0xFF for b in encrypted])
        with pytest.raises(Exception):
            EncryptionService.decrypt_file(tampered, iv)


class TestTLSEnforcer:

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
        SECURE_HSTS_SECONDS=31536000
    )
    def test_compliant_settings_pass(self):
        result = TLSEnforcer.check_settings()
        assert result['tls_compliant'] is True
        assert len(result['issues']) == 0

    @override_settings(
        SECURE_SSL_REDIRECT=False,
        SESSION_COOKIE_SECURE=False,
        CSRF_COOKIE_SECURE=False,
        SECURE_HSTS_SECONDS=0
    )
    def test_non_compliant_settings_lists_issues(self):
        result = TLSEnforcer.check_settings()
        assert result['tls_compliant'] is False
        assert len(result['issues']) >= 3
