# =============================================================================
# FILE: apps/edms/validators.py
# FIX #8: SHA-256 checksum computation removed from synchronous validator.
#   Previously the full file was read twice (magic check + sha256) inside the
#   request thread, blocking the worker for up to 3-4 seconds on 50 MB files.
#   Now validate_file_upload() only performs:
#     1. File size check
#     2. MIME type check (Content-Type header)
#     3. Magic bytes check (cannot be spoofed)
#   Checksum is scheduled as an async Celery task in FileAttachmentSerializer.
# =============================================================================
from django.conf import settings
from django.core.exceptions import ValidationError

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/bmp',
}

MAGIC_BYTES: dict[str, list[bytes]] = {
    'application/pdf': [b'%PDF'],
    'image/jpeg':      [b'\xff\xd8\xff'],
    'image/png':       [b'\x89PNG'],
    'image/tiff':      [b'II*\x00', b'MM\x00*'],
    'image/bmp':       [b'BM'],
}

MAX_UPLOAD_MB: int = getattr(settings, 'MAX_UPLOAD_MB', 50)


def validate_file_upload(file_obj) -> None:
    """Validate an uploaded file: size, MIME type, and magic bytes.
    Returns None. SHA-256 checksum is computed async after upload.
    Raises ValidationError on any failure.
    """
    # 1. Size check
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    if file_obj.size > max_bytes:
        raise ValidationError(
            f'File too large. Maximum allowed size is {MAX_UPLOAD_MB} MB '
            f'(uploaded: {file_obj.size / 1024 / 1024:.1f} MB).'
        )

    # 2. MIME type check
    content_type = getattr(file_obj, 'content_type', '').split(';')[0].strip().lower()
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f'File type "{content_type}" is not allowed. '
            f'Allowed types: {sorted(ALLOWED_MIME_TYPES)}.'
        )

    # 3. Magic bytes check
    file_obj.seek(0)
    header = file_obj.read(8)
    file_obj.seek(0)
    valid_signatures = MAGIC_BYTES.get(content_type, [])
    if valid_signatures:
        if not any(header.startswith(sig) for sig in valid_signatures):
            raise ValidationError(
                f'File content does not match declared type "{content_type}". '
                 'The file may be corrupted or misnamed.'
            )
