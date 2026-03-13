# =============================================================================
# FILE: apps/workledger/permissions.py
# FIX:  Replaced dual role string constants with unified core.User.Role.
#       Previously used lowercase 'admin','officer','engineer','viewer' which
#       never matched core.User.Role values (ADMIN, SECTION_HEAD, etc.).
#       Section Heads were effectively locked out of all work ledger writes.
# =============================================================================
from rest_framework.permissions import BasePermission
from apps.core.models import User


def get_user_role(request) -> str:
    """Return normalised role string from request.user.
    Always references core.User.Role constants - single source of truth.
    """
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        return getattr(request.user, 'role', User.Role.VIEWER)
    return User.Role.VIEWER


# Convenience aliases so views don't need to import User.Role directly
ROLE_ADMIN        = User.Role.ADMIN
ROLE_SECTION_HEAD = User.Role.SECTION_HEAD
ROLE_ENGINEER     = User.Role.ENGINEER
ROLE_LDO_STAFF    = User.Role.LDO_STAFF
ROLE_AUDIT        = User.Role.AUDIT
ROLE_VIEWER       = User.Role.VIEWER
# Keep backward-compat alias used in dropdown_views.py
ROLE_OFFICER      = User.Role.SECTION_HEAD
ROLE_ADMIN_STR    = User.Role.ADMIN  # used in dropdown_views require_admin check


class CanCreateWorkEntry(BasePermission):
    """Engineers, LDO Staff, Section Heads and Admins can create entries."""
    ALLOWED = [
        User.Role.ADMIN,
        User.Role.SECTION_HEAD,
        User.Role.ENGINEER,
        User.Role.LDO_STAFF,
    ]

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_user_role(request) in self.ALLOWED
        )


class CanEditWorkEntry(BasePermission):
    """Section Heads and Admins can edit any entry; Engineers only their own."""
    FULL_ACCESS = [User.Role.ADMIN, User.Role.SECTION_HEAD]

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        role = get_user_role(request)
        if role in self.FULL_ACCESS:
            return True
        if role == User.Role.ENGINEER:
            return obj.engineer_id == request.user.id
        return False


class CanExportReports(BasePermission):
    """Section Heads and Admins can export."""
    ALLOWED = [User.Role.ADMIN, User.Role.SECTION_HEAD]

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_user_role(request) in self.ALLOWED
        )


class CanManageDropdowns(BasePermission):
    """Only Admins can manage dropdown master data."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_user_role(request) == User.Role.ADMIN
        )
