# =============================================================================
# FILE: apps/workledger/dropdown_urls.py
# PURPOSE: URL routes for dropdown management
# =============================================================================
from django.urls import path
from . import dropdown_views as views

# Public routes (all authenticated users)
public_patterns = [
    path('',                          views.DropdownAllGroupsView.as_view(),    name='dropdown-all'),
    path('<str:group_key>/',          views.DropdownGroupView.as_view(),        name='dropdown-group'),
]

# Admin-only routes
admin_patterns = [
    path('<str:group_key>/',
         views.AdminDropdownGroupView.as_view(),         name='admin-dropdown-group'),
    path('<str:group_key>/<int:item_id>/',
         views.AdminDropdownItemView.as_view(),          name='admin-dropdown-item'),
    path('<str:group_key>/audit-log/',
         views.AdminDropdownAuditLogView.as_view(),      name='admin-dropdown-audit'),
]

# Mount in root urls.py:
# path('api/dropdowns/',       include(('apps.workledger.dropdown_urls', 'dropdowns'), 'public_patterns'))
# path('api/admin/dropdowns/', include(('apps.workledger.dropdown_urls', 'dropdowns'), 'admin_patterns'))
