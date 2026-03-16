# =============================================================================
# FILE: apps/rbac/permissions.py
# DRF permission classes that use RBACService
# Usage: permission_classes = [IsAuthenticated, HasDocumentPermission('doc.approve')]
# =============================================================================
from rest_framework.permissions import BasePermission
from .services import RBACService
from .models import Permission


class HasPermission(BasePermission):
    """Generic RBAC permission check. Pass permission string to constructor."""

    def __init__(self, permission: str):
        self.permission = permission

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return RBACService.has_permission(request.user, self.permission)


class CanCreateDocument(BasePermission):
    def has_permission(self, request, view):
        return RBACService.has_permission(request.user, Permission.DOC_CREATE)


class CanApproveDocument(BasePermission):
    def has_permission(self, request, view):
        return RBACService.has_permission(request.user, Permission.DOC_APPROVE)


class CanSignDocument(BasePermission):
    def has_permission(self, request, view):
        return RBACService.has_permission(request.user, Permission.DOC_SIGN)


class CanManageUsers(BasePermission):
    def has_permission(self, request, view):
        return RBACService.has_permission(request.user, Permission.USER_MANAGE)


class CanReadAudit(BasePermission):
    def has_permission(self, request, view):
        return RBACService.has_permission(request.user, Permission.AUDIT_READ)


class IsAuditor(BasePermission):
    """Auditor role — read-only access to docs + audit logs."""
    def has_permission(self, request, view):
        from .models import Role
        roles = RBACService.get_active_roles(request.user)
        return Role.AUDITOR in roles or Role.SYSTEM_ADMIN in roles
