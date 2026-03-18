# =============================================================================
# FILE: apps/search/exceptions.py
# Centralised exception types for the search app.
# Using custom exceptions avoids catching broad Exception in views.
# =============================================================================


class SearchUnavailableError(Exception):
    """Raised when a required DB extension (pg_trgm) is missing or the
    statement_timeout fires. The view catches this and returns HTTP 503
    with a graceful JSON body instead of a 500 traceback."""
