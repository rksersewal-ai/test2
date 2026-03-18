# =============================================================================
# FILE: apps/edms/views_search_deprecation.py
#
# Mixin that adds RFC 8594 Deprecation headers to the old document search
# endpoint (GET /api/v1/edms/documents/search/).
#
# WHY: The old endpoint uses DocumentRepository.fulltext_search() which does
# NOT include OCR text in results. The new unified endpoint
# GET /api/v1/search/unified/ includes OCR full-text. Returning both produces
# different result sets for the same query, confusing engineers.
#
# PLAN:
#   Phase 1 (now)   — Add Deprecation header. Frontend sees it in DevTools.
#   Phase 2         — Update frontend to call /search/unified/ exclusively.
#   Phase 3         — Remove the old endpoint entirely.
#
# USAGE: Add DeprecatedSearchMixin before the ViewSet base class:
#   class DocumentViewSet(DeprecatedSearchMixin, viewsets.ModelViewSet):
#       ...
#       @action(...)
#       def search(self, request):
#           response = super_search(request)   # original logic
#           return self.add_deprecation_headers(response)
# =============================================================================


DEPRECATION_DATE = 'Wed, 01 Jul 2026 00:00:00 GMT'
SUNSET_DATE      = 'Tue, 01 Sep 2026 00:00:00 GMT'
SUCCESSOR_URL   = '/api/v1/search/unified/'


class DeprecatedSearchMixin:
    """
    Adds RFC 8594 Deprecation + Sunset + Link headers to any response
    returned by a view method wrapped with add_deprecation_headers().

    These headers are visible in browser DevTools → Network tab → Response
    headers. They signal to the frontend team that this endpoint will be
    removed on SUNSET_DATE.
    """

    def add_deprecation_headers(self, response):
        response['Deprecation']  = DEPRECATION_DATE
        response['Sunset']       = SUNSET_DATE
        response['Link']         = (
            f'<{SUCCESSOR_URL}>; rel="successor-version", '
            f'<https://github.com/rksersewal-ai/test2/blob/main/docs/search_migration.md>'
            f'; rel="deprecation"'
        )
        return response
