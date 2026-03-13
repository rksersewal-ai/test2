from rest_framework.permissions import BasePermission


ROLE_ADMIN = "admin"
ROLE_OFFICER = "officer"
ROLE_ENGINEER = "engineer"
ROLE_VIEWER = "viewer"


def get_user_role(request) -> str:
    # Expects request.user.role or request.auth payload 'role'
    if hasattr(request.user, "role"):
        return request.user.role
    return getattr(request.auth, "get", lambda k, d: d)("role", ROLE_VIEWER)


class CanCreateWorkEntry(BasePermission):
    """Engineers and Officers can create entries."""
    def has_permission(self, request, view):
        return get_user_role(request) in [ROLE_ADMIN, ROLE_OFFICER, ROLE_ENGINEER]


class CanEditWorkEntry(BasePermission):
    """Officers and Admins can edit any entry; engineers only their own."""
    def has_object_permission(self, request, view, obj):
        role = get_user_role(request)
        if role in [ROLE_ADMIN, ROLE_OFFICER]:
            return True
        return obj.engineer_id == request.user.id


class CanExportReports(BasePermission):
    """Officers and Admins can export."""
    def has_permission(self, request, view):
        return get_user_role(request) in [ROLE_ADMIN, ROLE_OFFICER]
