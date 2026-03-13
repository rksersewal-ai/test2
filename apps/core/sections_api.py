# =============================================================================
# FILE: apps/core/sections_api.py
# FIX (#11): Expose core_section as a public read-only API endpoint.
#            The frontend DropdownSelect for 'section' group_key must call
#            GET /api/core/sections/ instead of /api/dropdowns/section/
#            (dropdown_master no longer contains the 'section' group).
# =============================================================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.models import Section


class SectionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all active sections sorted alphabetically by name."""
        sections = Section.objects.filter(is_active=True).order_by('name').values(
            'id', 'code', 'name', 'description'
        )
        return Response(list(sections))
