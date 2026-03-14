# =============================================================================
# FILE: backend/edms/pagination.py
# CUSTOM PAGINATION CLASS
#
# Adds `total_count` and `total_pages` to every paginated list response.
# This matches the PaginatedResponse<T> TypeScript type in frontend/src/api/types.ts
# which services and pages use for correct page count calculation.
#
# Default DRF PageNumberPagination only returns `count`, `next`, `previous`.
# Pages were computing totalPages as Math.ceil(total / PAGE_SIZE) but `total`
# was undefined because the key didn't exist — causing NaN page counts.
# =============================================================================
import math
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class EDMSPageNumberPagination(PageNumberPagination):
    page_size             = 25
    page_size_query_param = 'page_size'
    max_page_size         = 200

    def get_paginated_response(self, data):
        page_size   = self.get_page_size(self.request) or self.page_size
        total_count = self.page.paginator.count
        total_pages = math.ceil(total_count / page_size) if page_size else 1

        return Response({
            'count'      : total_count,
            'total_count': total_count,   # alias — matches frontend TS type
            'total_pages': total_pages,
            'page_size'  : page_size,
            'next'       : self.get_next_link(),
            'previous'   : self.get_previous_link(),
            'results'    : data,
        })

    def get_paginated_response_schema(self, schema):
        """OpenAPI schema support."""
        return {
            'type': 'object',
            'required': ['count', 'total_count', 'total_pages', 'results'],
            'properties': {
                'count'      : {'type': 'integer'},
                'total_count': {'type': 'integer'},
                'total_pages': {'type': 'integer'},
                'page_size'  : {'type': 'integer'},
                'next'       : {'type': 'string', 'nullable': True},
                'previous'   : {'type': 'string', 'nullable': True},
                'results'    : schema,
            },
        }
