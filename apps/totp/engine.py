# =============================================================================
# FILE: apps/totp/engine.py
# SPRINT 8 — TOTP core logic (RFC 6238)
#
# Uses pyotp (pure-Python, no internet) for TOTP generation + verification.
# QR code generated with qrcode library into a PNG data URI — shown once
# at setup time, never stored on disk.
#
# Token window: ±1 step (30 s tolerance for clock skew on LAN devices)
# Issuer name: 'PLW EDMS' (appears in authenticator app)
# =============================================================================
import base64
import io
import secrets
import logging

import pyotp

log    = logging.getLogger('totp')
ISSUER = 'PLW EDMS'


def generate_secret() -> str:
    """Generate a new base32 TOTP secret (20 bytes = 160 bits)."""
    return pyotp.random_base32()


def get_totp(secret: str) -> pyotp.TOTP:
    return pyotp.TOTP(secret, issuer=ISSUER)


def verify_code(secret: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a 6-digit TOTP code.
    valid_window=1 accepts current ±1 interval (90-second window total).
    """
    try:
        return get_totp(secret).verify(code.strip(), valid_window=valid_window)
    except Exception:
        return False


def provisioning_uri(secret: str, username: str) -> str:
    """Return the otpauth:// URI for QR code generation."""
    return get_totp(secret).provisioning_uri(
        name=username, issuer_name=ISSUER
    )


def qr_png_data_uri(secret: str, username: str) -> str:
    """
    Return a base64 data URI of the QR code PNG.
    Rendered entirely in memory — never written to disk.
    """
    import qrcode
    uri = provisioning_uri(secret, username)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'data:image/png;base64,{b64}'
