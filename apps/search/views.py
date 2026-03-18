# =============================================================================
# FILE: apps/search/views.py
#
# Two APIView endpoints (not ViewSets — no router needed, simpler routing):
#
#   GET /api/v1/search/autocomplete/?q=WAG9&limit=10
#     - Minimum 2 chars enforced
#     - Returns list of lightweight suggestions
#     - HTTP 503 on timeout / missing pg_trgm (graceful degradation)
#
#   GET /api/v1/search/unified/?q=WAG9+drawing&page=1&page_size=25
#     - Minimum 2 chars enforced
#     - Returns paginated ranked cross-entity results
#     - HTTP 503 on timeout
#
# PRODUCTION SAFETY:
#   - Both endpoints are GET-only, authenticated (IsAuthenticated)
#   - No write operations possible
#   - SearchUnavailableError → HTTP 503 + descriptive JSON (never 500)
#   - All DB timeouts are LOCAL (transaction-scoped) — no global side effects
#   - Exceptions are logged with WARNING level (not ERROR) since these are
#     expected degradation paths, not application bugs
# =============================================================================
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.search.repository import autocomplete_search, unified_search
from apps.search.exceptions import SearchUnavailableError

logger = logging.getLogger(__name__)

_MIN_QUERY_LEN = 2   # Prevents full-table scans on single chars
_MAX_LIMIT     = 50  # Autocomplete hard ceiling
_MAX_PAGE_SIZE = 100 # Unified search page ceiling


class AutocompleteView(APIView):
    """
    GET /api/v1/search/autocomplete/?q=<term>&limit=<n>

    Typeahead endpoint. Returns up to `limit` (default 10, max 50)
    lightweight document suggestions as the user types.

    Response shape:
        [
          {
            "id": 42,
            "document_number": "PLW/ELE/001",
            "title": "WAG-9 Electrical Schematic",
            "status": "ACTIVE",
            "file_name": null,
            "file_type": null,
            "match_source": "document",
            "rank": 1.0
          },
          ...
        ]
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names  = ['get', 'head', 'options']

    def get(self, request):
        q     = request.query_params.get('q', '').strip()
        limit = request.query_params.get('limit', 10)

        if len(q) < _MIN_QUERY_LEN:
            return Response(
                {'error': f'Query must be at least {_MIN_QUERY_LEN} characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            limit = max(1, min(int(limit), _MAX_LIMIT))
        except (ValueError, TypeError):
            limit = 10

        try:
            results = autocomplete_search(q=q, limit=limit)
        except SearchUnavailableError as exc:
            logger.warning('autocomplete_search degraded: %s', exc)
            return Response(
                {'error': str(exc), 'results': []},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as exc:
            logger.error('autocomplete_search unexpected error: %s', exc, exc_info=True)
            return Response(
                {'error': 'Search temporarily unavailable. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(results)


class UnifiedSearchView(APIView):
    """
    GET /api/v1/search/unified/?q=<term>&page=1&page_size=25

    Full cross-entity ranked search. Searches document metadata, filenames,
    OCR full text, document notes, and correspondent names in one call.

    Response shape:
        {
          "count":   150,
          "page":    1,
          "pages":   6,
          "page_size": 25,
          "results": [
            {
              "id": 42,
              "document_number": "PLW/ELE/001",
              "title": "WAG-9 Electrical Schematic",
              "status": "ACTIVE",
              "file_name": "WAG9_Elec_Rev3.pdf",
              "file_type": "PDF",
              "match_source": "doc_number",
              "snippet": null,
              "rank": 5.0
            },
            ...
          ]
        }
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names  = ['get', 'head', 'options']

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if len(q) < _MIN_QUERY_LEN:
            return Response(
                {'error': f'Query must be at least {_MIN_QUERY_LEN} characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            page      = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(int(request.query_params.get('page_size', 25)), _MAX_PAGE_SIZE))
        except (ValueError, TypeError):
            page      = 1
            page_size = 25

        offset = (page - 1) * page_size

        try:
            data = unified_search(q=q, limit=page_size, offset=offset)
        except SearchUnavailableError as exc:
            logger.warning('unified_search degraded: %s', exc)
            return Response(
                {'error': str(exc), 'count': 0, 'results': []},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as exc:
            logger.error('unified_search unexpected error: %s', exc, exc_info=True)
            return Response(
                {'error': 'Search temporarily unavailable. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        total      = data.get('count', 0)
        pages      = max(1, -(-total // page_size))  # ceiling division
        return Response({
            'count':     total,
            'page':      page,
            'pages':     pages,
            'page_size': page_size,
            'results':   data.get('results', []),
        })
