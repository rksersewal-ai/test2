"""RBAC permission classes - PLW EDMS + LDO."""
from rest_framework.permissions import BasePermission
from apps.core.models import User


class IsAdminRole(BasePermission):
    """Only ADMIN role users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN)


class IsAdminOrSectionHead(BasePermission):
    """ADMIN or SECTION_HEAD."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in [User.Role.ADMIN, User.Role.SECTION_HEAD]
        )


class IsEngineerOrAbove(BasePermission):
    """ENGINEER, SECTION_HEAD, ADMIN, LDO_STAFF."""
    ALLOWED = [User.Role.ENGINEER, User.Role.SECTION_HEAD, User.Role.ADMIN, User.Role.LDO_STAFF]

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in self.ALLOWED
        )


class IsAuditRole(BasePermission):
    """AUDIT or ADMIN role - read-only audit access."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in [User.Role.AUDIT, User.Role.ADMIN]
        )


class ReadOnly(BasePermission):
    """Safe methods only."""
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
