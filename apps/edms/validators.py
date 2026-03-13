# =============================================================================
# FILE: apps/edms/validators.py
# FIX (#2): File upload validation - MIME type whitelist + max size check
#           + magic bytes verification (prevents MIME spoofing)
# =============================================================================
import os
import hashlib
from django.conf import settings
from rest_framework.exceptions import ValidationError

# Allowed MIME types for uploaded documents
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/bmp',
}

# Magic byte signatures for allowed file types
MAGIC_BYTES: dict[str, bytes] = {
    'pdf':  b'%PDF',
    'jpeg': b'\xff\xd8\xff',
    'png':  b'\x89PNG',
    'tiff_le': b'II*\x00',
    'tiff_be': b'MM\x00*',
    'bmp':  b'BM',
}

# Default max upload: 50 MB. Override in settings: MAX_UPLOAD_MB = 100
DEFAULT_MAX_MB = 50


def _max_bytes() -> int:
    return int(getattr(settings, 'MAX_UPLOAD_MB', DEFAULT_MAX_MB)) * 1024 * 1024


def validate_document_file(file) -> None:
    """Validate uploaded file: MIME type, magic bytes, and size.
    Raises ValidationError on any violation.
    """
    # 1. Size check
    max_bytes = _max_bytes()
    if file.size > max_bytes:
        raise ValidationError(
            f'File too large. Maximum allowed size is '
            f'{getattr(settings, "MAX_UPLOAD_MB", DEFAULT_MAX_MB)} MB. '
            f'Uploaded file is {file.size / (1024*1024):.1f} MB.'
        )

    # 2. MIME type check (content_type header)
    content_type = getattr(file, 'content_type', '').lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f'File type "{content_type}" is not allowed. '
            f'Allowed types: PDF, JPEG, PNG, TIFF, BMP.'
        )

    # 3. Magic bytes check (prevents MIME spoofing)
    file.seek(0)
    header = file.read(8)
    file.seek(0)
    magic_ok = any(header.startswith(sig) for sig in MAGIC_BYTES.values())
    if not magic_ok:
        raise ValidationError(
            'File content does not match an allowed document type. '
            'Upload only genuine PDF, JPEG, PNG, or TIFF files.'
        )

    # 4. Filename extension check
    name = getattr(file, 'name', '')
    ext = os.path.splitext(name)[1].lower()
    allowed_exts = {'.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}
    if ext and ext not in allowed_exts:
        raise ValidationError(
            f'File extension "{ext}" is not allowed. '
            f'Allowed extensions: {sorted(allowed_exts)}.'
        )


def compute_sha256(file) -> str:
    """Compute SHA-256 checksum of an uploaded file. Rewinds file after reading."""
    sha = hashlib.sha256()
    file.seek(0)
    for chunk in iter(lambda: file.read(8192), b''):
        sha.update(chunk)
    file.seek(0)
    return sha.hexdigest()
