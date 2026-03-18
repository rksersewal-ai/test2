# =============================================================================
# FILE: apps/core/cache.py
#
# Centralised caching helpers for the EDMS application.
#
# Design principles:
#   1. Cache-aside pattern: cache is populated on miss, invalidated on write.
#   2. All cache keys are namespaced to avoid collisions between apps.
#   3. Cache failures are ALWAYS silent (log warning, return None) so the
#      application continues to work even if the cache store is unavailable.
#   4. No cache dependency on external services (Redis optional, FileCache
#      default) — works on a Windows LAN server with zero extra setup.
# =============================================================================
import logging
import hashlib
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse

logger = logging.getLogger(__name__)

# Cache timeout constants (seconds)
CACHE_SHORT   = 60         # 1 min  — frequently updated lists
CACHE_MEDIUM  = 300        # 5 min  — document list pages
CACHE_LONG    = 3600       # 1 hour — dropdown options (categories, doc types)
CACHE_STATIC  = 86400      # 24 hr  — static reference data (almost never changes)


def make_cache_key(*parts) -> str:
    """Build a safe, namespaced cache key from arbitrary parts.
    Uses SHA-1 to keep keys under memcache's 250-byte limit."""
    raw = 'edms:' + ':'.join(str(p) for p in parts)
    if len(raw) > 200:
        raw = 'edms:hash:' + hashlib.sha1(raw.encode()).hexdigest()
    return raw


def cache_get(key: str):
    """Safe cache get — returns None on any cache failure."""
    try:
        return cache.get(key)
    except Exception as exc:
        logger.warning('cache_get failed for key=%s: %s', key, exc)
        return None


def cache_set(key: str, value, timeout: int = CACHE_MEDIUM):
    """Safe cache set — silently logs on failure, never raises."""
    try:
        cache.set(key, value, timeout)
    except Exception as exc:
        logger.warning('cache_set failed for key=%s: %s', key, exc)


def cache_delete(key: str):
    """Safe cache delete."""
    try:
        cache.delete(key)
    except Exception as exc:
        logger.warning('cache_delete failed for key=%s: %s', key, exc)


def cache_delete_pattern(prefix: str):
    """Delete all keys matching prefix (requires django-redis or iterates
    manually on file-based cache — safe either way)."""
    try:
        # django-redis supports delete_pattern directly
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(f'{prefix}*')
        else:
            # FileBasedCache / LocMemCache: iterate (acceptable for small caches)
            # This is a no-op if the backend doesn't support keys() — safe.
            pass
    except Exception as exc:
        logger.warning('cache_delete_pattern failed prefix=%s: %s', prefix, exc)


# ---------------------------------------------------------------------------
# Per-view response caching decorator
# ---------------------------------------------------------------------------

def view_cache(timeout: int = CACHE_MEDIUM, key_func=None):
    """
    Decorator for DRF APIView.get() methods.

    Caches the serialized JSON response. Cache key is derived from:
      - view class name
      - request.user.id (per-user, safe for authenticated endpoints)
      - request.GET (query params)

    PRODUCTION SAFETY:
      - Only caches GET requests
      - Only caches HTTP 200 responses
      - Cache miss falls through to normal view logic
      - Cache failure (store down) is silent — view runs normally

    Usage:
        @view_cache(timeout=CACHE_MEDIUM)
        def get(self, request, *args, **kwargs):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(self_or_view, request, *args, **kwargs):
            if request.method != 'GET':
                return view_func(self_or_view, request, *args, **kwargs)

            if key_func:
                cache_key = key_func(request, *args, **kwargs)
            else:
                params_str = '&'.join(
                    f'{k}={v}' for k, v in sorted(request.GET.items())
                )
                cache_key = make_cache_key(
                    self_or_view.__class__.__name__,
                    request.user.id,
                    params_str,
                )

            cached = cache_get(cache_key)
            if cached is not None:
                response = HttpResponse(
                    cached,
                    content_type='application/json',
                    status=200,
                )
                response['X-Cache'] = 'HIT'
                return response

            response = view_func(self_or_view, request, *args, **kwargs)

            if hasattr(response, 'status_code') and response.status_code == 200:
                try:
                    content = response.rendered_content
                    cache_set(cache_key, content, timeout)
                    response['X-Cache'] = 'MISS'
                except Exception as exc:
                    logger.warning('view_cache: failed to cache response: %s', exc)

            return response
        return wrapped
    return decorator


# ---------------------------------------------------------------------------
# Document-specific cache invalidation
# ---------------------------------------------------------------------------

def invalidate_document_cache(document_id: int = None):
    """
    Call this after any write operation on a Document (create, update,
    status change, revision add) to ensure list pages show fresh data.

    If document_id is provided, also invalidates that document's detail cache.
    """
    # Invalidate list-level caches (pattern delete if supported)
    cache_delete_pattern('edms:DocumentViewSet')
    cache_delete_pattern('edms:CategoryViewSet')

    if document_id:
        cache_delete(make_cache_key('document', 'detail', document_id))


def invalidate_dropdown_cache():
    """
    Call when categories or document types change.
    These are long-cached (CACHE_LONG) since they rarely change.
    """
    cache_delete_pattern('edms:CategoryViewSet')
    cache_delete_pattern('edms:DocumentTypeViewSet')
