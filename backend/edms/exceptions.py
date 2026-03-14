# =============================================================================
# FILE: backend/edms/exceptions.py
# CUSTOM DRF EXCEPTION HANDLER
#
# Problem: Default DRF exception handler returns different shapes for
#   different error types — plain strings, lists, dicts, HTML 500 pages.
#   Frontend pages then crash on response.data.detail or similar.
#
# Solution: Uniform JSON envelope for EVERY error response:
#   {
#     "status"      : 400,
#     "code"        : "validation_error",
#     "detail"      : "Human-readable summary",
#     "field_errors": { "field": ["msg"] },
#     "timestamp"   : "2026-03-14T14:30:00+05:30"
#   }
# =============================================================================
import logging
from datetime import datetime, timezone
from django.utils import timezone as dj_timezone
from rest_framework.views import exception_handler as drf_default_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('edms.exceptions')


def edms_exception_handler(exc, context):
    """Uniform JSON error body for every DRF exception + unhandled 500."""
    # Let DRF do its normal processing first
    response = drf_default_handler(exc, context)

    now_iso = dj_timezone.now().isoformat()

    if response is not None:
        data        = response.data
        field_errors: dict = {}
        detail      = 'An error occurred.'
        code        = getattr(exc, 'default_code', 'error')

        if isinstance(data, dict):
            # Extract field-level validation errors
            for key, val in data.items():
                if key in ('detail', 'code'):
                    continue
                if isinstance(val, list):
                    field_errors[key] = [str(v) for v in val]
                elif isinstance(val, str):
                    field_errors[key] = [val]

            if 'detail' in data:
                raw_detail = data['detail']
                detail = str(raw_detail) if not hasattr(raw_detail, 'code') else raw_detail.args[0] if raw_detail.args else str(raw_detail)
            elif field_errors:
                # Construct a readable summary from first field error
                first_field = next(iter(field_errors))
                detail = f"{first_field}: {field_errors[first_field][0]}"

            if 'code' in data:
                code = str(data['code'])

        elif isinstance(data, list):
            # Non-field errors returned as list
            detail = '; '.join(str(x) for x in data)
            field_errors['non_field_errors'] = [str(x) for x in data]

        elif isinstance(data, str):
            detail = data

        response.data = {
            'status'      : response.status_code,
            'code'        : code,
            'detail'      : detail,
            'field_errors': field_errors,
            'timestamp'   : now_iso,
        }

        # Log 5xx server errors so they appear in edms.log
        if response.status_code >= 500:
            view = context.get('view')
            logger.error(
                'Server error %s in %s: %s',
                response.status_code,
                view.__class__.__name__ if view else 'unknown',
                detail,
                exc_info=exc,
            )

        return response

    # Unhandled exception — DRF returned None (propagated as HTTP 500)
    logger.exception('Unhandled exception in API view: %s', exc)
    return Response({
        'status'      : 500,
        'code'        : 'server_error',
        'detail'      : 'Internal server error. Check server logs.',
        'field_errors': {},
        'timestamp'   : now_iso,
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
