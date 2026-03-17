# =============================================================================
# FILE: apps/ocr/throttles.py
# FIX #19b: Per-user rate throttle for OCR queue submission.
#
# Limits:
#   OCRSubmitThrottle   — 20 submissions / hour per authenticated user
#   OCRRetryThrottle    — 10 retries    / hour per authenticated user
#
# These are deliberately conservative for a LAN-deployed enterprise system.
# Override via settings.py:
#   REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['ocr_submit'] = '50/hour'
# =============================================================================
from rest_framework.throttling import UserRateThrottle


class OCRSubmitThrottle(UserRateThrottle):
    """
    Throttle for OCR job submission (POST to /api/v1/ocr/queue/).
    Prevents a single user from saturating all Celery workers by queuing
    hundreds of large files in rapid succession.
    Rate: 20 submissions per hour per user (configurable via settings).
    """
    scope = 'ocr_submit'


class OCRRetryThrottle(UserRateThrottle):
    """
    Throttle for manual OCR retry action (POST to /api/v1/ocr/queue/{id}/retry/).
    Prevents hammering the retry endpoint when Tesseract is mis-configured.
    Rate: 10 retries per hour per user (configurable via settings).
    """
    scope = 'ocr_retry'
