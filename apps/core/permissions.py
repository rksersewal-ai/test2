# =============================================================================
# FILE: apps/core/permissions.py
# FIX (#1): Unified RBAC — single source of truth for ALL apps.
#           apps/workledger/permissions.py now imports from here.
#           Mapping: SECTION_HEAD = officer-level access.
# =============================================================================
from rest_framework.permissions import BasePermission
from apps.core.models import User

# ---- Canonical role aliases used across all apps ----
ROLE_ADMIN        = User.Role.ADMIN          # 'ADMIN'
ROLE_SECTION_HEAD = User.Role.SECTION_HEAD   # 'SECTION_HEAD'  ← was 'officer' (BROKEN)
ROLE_ENGINEER     = User.Role.ENGINEER       # 'ENGINEER'
ROLE_LDO_STAFF    = User.Role.LDO_STAFF      # 'LDO_STAFF'
ROLE_AUDIT        = User.Role.AUDIT          # 'AUDIT'
ROLE_VIEWER       = User.Role.VIEWER         # 'VIEWER'

# Convenience sets
OFFICER_AND_ABOVE = {ROLE_ADMIN, ROLE_SECTION_HEAD}
ENGINEER_AND_ABOVE = {ROLE_ADMIN, ROLE_SECTION_HEAD, ROLE_ENGINEER, ROLE_LDO_STAFF}


def get_user_role(request) -> str:
    """Return the canonical role string from the authenticated user.
    Always reads from request.user (Django User model), never from JWT payload,
    to prevent role-claim spoofing.
    """
    if request.user and request.user.is_authenticated:
        return request.user.role
    return ROLE_VIEWER


# ---- Core permission classes ----

class IsAdminRole(BasePermission):
    """Only ADMIN role."""
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and get_user_role(request) == ROLE_ADMIN
        )


class IsAdminOrSectionHead(BasePermission):
    """ADMIN or SECTION_HEAD (officer-level)."""
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and get_user_role(request) in OFFICER_AND_ABOVE
        )


class IsEngineerOrAbove(BasePermission):
    """ENGINEER, SECTION_HEAD, ADMIN, LDO_STAFF."""
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and get_user_role(request) in ENGINEER_AND_ABOVE
        )


class IsAuditRole(BasePermission):
    """AUDIT or ADMIN — read-only audit access."""
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and get_user_role(request) in {ROLE_AUDIT, ROLE_ADMIN}
        )


class ReadOnly(BasePermission):
    """Safe methods only (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')


# ---- Work Ledger specific permission classes (FIX #1: moved here from workledger/permissions.py) ----

class CanCreateWorkEntry(BasePermission):
    """Engineers, Section Heads, LDO Staff, and Admins can create entries."""
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and get_user_role(request) in ENGINEER_AND_ABOVE
        )


class CanEditWorkEntry(BasePermission):
    """Section Heads and Admins can edit any entry; engineers only their own."""
    def has_object_permission(self, request, view, obj):
        role = get_user_role(request)
        if role in OFFICER_AND_ABOVE:
            return True
        # Engineer/LDO_Staff can edit only their own entries
        return obj.engineer_id == request.user.id


class CanExportReports(BasePermission):
    """Section Heads and Admins can export reports."""
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and get_user_role(request) in OFFICER_AND_ABOVE
        )


class CanManageDropdowns(BasePermission):
    """Only ADMIN can manage dropdown master data."""
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and get_user_role(request) == ROLE_ADMIN
        )
