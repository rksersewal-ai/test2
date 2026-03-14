# =============================================================================
# FILE: apps/work_ledger/permissions.py
# =============================================================================
from rest_framework.permissions import BasePermission, SAFE_METHODS


SUPERVISOR_ROLES = {'ADMIN', 'OFFICER', 'WM', 'SSE'}


class IsSupervisorOrAbove(BasePermission):
    """Allow access only to supervisors, WMs, Officers, and Admins."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        role_name = getattr(role, 'role_name', str(role)).upper() if role else ''
        return request.user.is_staff or role_name in SUPERVISOR_ROLES


class IsOwnerOrSupervisor(BasePermission):
    """
    Object-level: allow if user owns the entry OR is a supervisor.
    Read-only is always allowed for authenticated users.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        if obj.user == request.user:
            return True
        role = getattr(request.user, 'role', None)
        role_name = getattr(role, 'role_name', str(role)).upper() if role else ''
        return role_name in SUPERVISOR_ROLES
