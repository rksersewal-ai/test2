# =============================================================================
# FILE: apps/sanity/views.py
# Health check endpoint: GET /api/v1/health/
#
# Returns HTTP 200 with JSON body when all systems are healthy.
# Returns HTTP 503 when DB or cache is unavailable.
#
# Used by:
#   - IIS Application Request Routing health probe
#   - Windows Task Scheduler monitoring script
#   - LAN monitoring tools (PRTG, Zabbix, simple curl)
#
# Response format:
#   {
#     "status": "ok" | "degraded",
#     "db":     "ok" | "error: <message>",
#     "cache":  "ok" | "error: <message>",
#     "version": "1.0"
#   }
#
# Authentication: NOT required — health check must work before login.
# Rate limit:     Minimal (LAN-only deployment; behind LanOnlyMiddleware).
# =============================================================================
import logging
from django.db import connection, OperationalError as DjDBError
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

APP_VERSION = '1.0'


def _check_db() -> str:
    """Ping PostgreSQL with SELECT 1. Returns 'ok' or 'error: <msg>'."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return 'ok'
    except DjDBError as exc:
        logger.error('Health check DB failure: %s', exc)
        return f'error: {exc}'
    except Exception as exc:
        logger.error('Health check DB unexpected error: %s', exc)
        return f'error: {exc}'


def _check_cache() -> str:
    """Ping the cache backend with a set/get round-trip. Returns 'ok' or 'error: <msg>'."""
    try:
        from django.core.cache import cache
        cache.set('__health_check__', '1', timeout=10)
        val = cache.get('__health_check__')
        if val != '1':
            return 'error: cache set/get mismatch'
        return 'ok'
    except Exception as exc:
        logger.error('Health check cache failure: %s', exc)
        return f'error: {exc}'


@api_view(['GET'])
@authentication_classes([])   # no auth required
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /api/v1/health/

    Lightweight health probe. Checks DB + cache in < 50ms.
    Returns 200 if healthy, 503 if degraded.
    """
    db_status    = _check_db()
    cache_status = _check_cache()

    all_ok   = (db_status == 'ok' and cache_status == 'ok')
    http_status = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    payload = {
        'status':  'ok' if all_ok else 'degraded',
        'db':      db_status,
        'cache':   cache_status,
        'version': APP_VERSION,
    }

    if not all_ok:
        logger.warning('Health check degraded: db=%s cache=%s', db_status, cache_status)

    return Response(payload, status=http_status)
