# =============================================================================
# FILE: apps/search/urls.py
# Registered at: /api/v1/search/  (wired in config/urls.py)
# =============================================================================
from django.urls import path
from apps.search.views import AutocompleteView, UnifiedSearchView

urlpatterns = [
    path('autocomplete/', AutocompleteView.as_view(),   name='search-autocomplete'),
    path('unified/',      UnifiedSearchView.as_view(),  name='search-unified'),
]
