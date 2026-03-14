# =============================================================================
# FILE: apps/workledger/permissions.py
# FIX (#1): This file now re-exports from apps.core.permissions.
#           DO NOT define role constants here — core.permissions is the
#           single source of truth for all roles across all apps.
# =============================================================================
from apps.core.permissions import (  # noqa: F401  (re-export)
    get_user_role,
    CanCreateWorkEntry,
    CanEditWorkEntry,
    CanExportReports,
    CanManageDropdowns,
    OFFICER_AND_ABOVE,
    ENGINEER_AND_ABOVE,
    ROLE_ADMIN,
    ROLE_SECTION_HEAD,
    ROLE_ENGINEER,
    ROLE_LDO_STAFF,
    ROLE_VIEWER,
)
