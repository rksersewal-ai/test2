# =============================================================================
# FILE: apps/rbac/services.py
# FR-009: RBAC permission checking engine
# Central service: has_permission(), get_user_roles(), assign_role(),
# revoke_role(), get_effective_permissions().
# =============================================================================
from django.utils import timezone
from .models import UserRole, DocumentPermissionOverride, Role, Permission, ROLE_PERMISSIONS
from apps.edms.models import Document


class RBACService:

    @staticmethod
    def get_active_roles(user, section=None, document_type=None) -> list[str]:
        """Return list of active role names for a user, optionally filtered by scope."""
        qs = UserRole.objects.filter(
            user=user, is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        )
        if section:
            qs = qs.filter(models.Q(section__isnull=True) | models.Q(section=section))
        if document_type:
            qs = qs.filter(
                models.Q(document_type__isnull=True) | models.Q(document_type=document_type)
            )
        return list(qs.values_list('role', flat=True))

    @staticmethod
    def get_effective_permissions(user, section=None, document_type=None) -> set[str]:
        """Return full set of permissions for a user given their roles."""
        roles  = RBACService.get_active_roles(user, section, document_type)
        perms  = set()
        for role in roles:
            perms.update(ROLE_PERMISSIONS.get(role, []))
        return perms

    @staticmethod
    def has_permission(
        user,
        permission: str,
        document: Document = None,
        section=None,
        document_type=None,
    ) -> bool:
        """Check if user has a specific permission, considering object-level overrides."""
        # 1. Check document-level DENY override first
        if document:
            try:
                override = DocumentPermissionOverride.objects.get(
                    user=user,
                    document=document,
                    permission=permission,
                    override=DocumentPermissionOverride.OverrideType.DENY
                )
                if not override.expires_at or override.expires_at > timezone.now():
                    return False
            except DocumentPermissionOverride.DoesNotExist:
                pass

            # 2. Check document-level GRANT override
            try:
                override = DocumentPermissionOverride.objects.get(
                    user=user,
                    document=document,
                    permission=permission,
                    override=DocumentPermissionOverride.OverrideType.GRANT
                )
                if not override.expires_at or override.expires_at > timezone.now():
                    return True
            except DocumentPermissionOverride.DoesNotExist:
                pass

        # 3. Fall back to role-based permissions
        section_obj      = section or (document.section if document else None)
        document_type_obj = document_type or (document.document_type if document else None)
        perms = RBACService.get_effective_permissions(user, section_obj, document_type_obj)
        return permission in perms

    @staticmethod
    def assign_role(
        user, role: str, granter=None, section=None,
        document_type=None, expires_at=None
    ) -> UserRole:
        ur, _ = UserRole.objects.update_or_create(
            user=user, role=role,
            section=section, document_type=document_type,
            defaults={
                'is_active': True,
                'granted_by': granter,
                'expires_at': expires_at,
            }
        )
        return ur

    @staticmethod
    def revoke_role(user, role: str, section=None, document_type=None):
        UserRole.objects.filter(
            user=user, role=role,
            section=section, document_type=document_type
        ).update(is_active=False)


# Import models here to avoid circular import
from django.db import models
