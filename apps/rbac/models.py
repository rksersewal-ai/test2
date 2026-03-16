# =============================================================================
# FILE: apps/rbac/models.py
# FR-009: Full RBAC — 8 roles as specified in PRD
# Roles: SYSTEM_ADMIN, DMS_ADMIN, SECTION_OFFICER, DEALING_CLERK,
#        DRAWING_OFFICER, REVIEWER, VIEWER, AUDITOR
# Supports section-level, document-type-level, and object-level permissions.
# =============================================================================
from django.db import models
from django.conf import settings
from apps.edms.models import Document, DocumentType
from apps.core.models import Section


class Role(models.TextChoices):
    SYSTEM_ADMIN    = 'SYSTEM_ADMIN',    'System Administrator'
    DMS_ADMIN       = 'DMS_ADMIN',       'DMS Administrator'
    SECTION_OFFICER = 'SECTION_OFFICER', 'Section Officer'
    DEALING_CLERK   = 'DEALING_CLERK',   'Dealing Clerk'
    DRAWING_OFFICER = 'DRAWING_OFFICER', 'Drawing Office Officer'
    REVIEWER        = 'REVIEWER',        'Reviewer'
    VIEWER          = 'VIEWER',          'Viewer'
    AUDITOR         = 'AUDITOR',         'Auditor (Read-only + Audit logs)'


class Permission(models.TextChoices):
    # Document permissions
    DOC_CREATE   = 'doc.create',   'Create Document'
    DOC_READ     = 'doc.read',     'Read Document'
    DOC_UPDATE   = 'doc.update',   'Update Document'
    DOC_DELETE   = 'doc.delete',   'Delete Document'
    DOC_APPROVE  = 'doc.approve',  'Approve Document'
    DOC_SIGN     = 'doc.sign',     'Digitally Sign Document'
    DOC_DOWNLOAD = 'doc.download', 'Download Document'
    DOC_SHARE    = 'doc.share',    'Share Document'
    # Admin permissions
    USER_MANAGE  = 'user.manage',  'Manage Users'
    AUDIT_READ   = 'audit.read',   'Read Audit Logs'
    SYSTEM_CONFIG= 'system.config','System Configuration'
    REPORT_VIEW  = 'report.view',  'View Reports'


# Default role-permission mapping per PRD
ROLE_PERMISSIONS: dict[str, list[str]] = {
    Role.SYSTEM_ADMIN: [
        Permission.DOC_CREATE, Permission.DOC_READ, Permission.DOC_UPDATE,
        Permission.DOC_DELETE, Permission.DOC_APPROVE, Permission.DOC_SIGN,
        Permission.DOC_DOWNLOAD, Permission.DOC_SHARE,
        Permission.USER_MANAGE, Permission.AUDIT_READ,
        Permission.SYSTEM_CONFIG, Permission.REPORT_VIEW,
    ],
    Role.DMS_ADMIN: [
        Permission.DOC_CREATE, Permission.DOC_READ, Permission.DOC_UPDATE,
        Permission.DOC_DELETE, Permission.DOC_APPROVE, Permission.DOC_SIGN,
        Permission.DOC_DOWNLOAD, Permission.DOC_SHARE,
        Permission.USER_MANAGE, Permission.AUDIT_READ, Permission.REPORT_VIEW,
    ],
    Role.SECTION_OFFICER: [
        Permission.DOC_CREATE, Permission.DOC_READ, Permission.DOC_UPDATE,
        Permission.DOC_APPROVE, Permission.DOC_SIGN,
        Permission.DOC_DOWNLOAD, Permission.DOC_SHARE, Permission.REPORT_VIEW,
    ],
    Role.DRAWING_OFFICER: [
        Permission.DOC_CREATE, Permission.DOC_READ, Permission.DOC_UPDATE,
        Permission.DOC_SIGN, Permission.DOC_DOWNLOAD, Permission.DOC_SHARE,
    ],
    Role.DEALING_CLERK: [
        Permission.DOC_CREATE, Permission.DOC_READ,
        Permission.DOC_DOWNLOAD, Permission.DOC_SHARE,
    ],
    Role.REVIEWER: [
        Permission.DOC_READ, Permission.DOC_DOWNLOAD,
    ],
    Role.VIEWER: [
        Permission.DOC_READ, Permission.DOC_DOWNLOAD,
    ],
    Role.AUDITOR: [
        Permission.DOC_READ, Permission.DOC_DOWNLOAD,
        Permission.AUDIT_READ, Permission.REPORT_VIEW,
    ],
}


class UserRole(models.Model):
    """Assigns a role to a user, optionally scoped to a Section or DocumentType."""

    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles'
    )
    role          = models.CharField(max_length=30, choices=Role.choices)
    section       = models.ForeignKey(
        Section, null=True, blank=True,
        on_delete=models.CASCADE, related_name='user_roles',
        help_text='If set, role applies only to this section'
    )
    document_type = models.ForeignKey(
        DocumentType, null=True, blank=True,
        on_delete=models.CASCADE, related_name='user_roles',
        help_text='If set, role applies only to this document type'
    )
    granted_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='roles_granted'
    )
    granted_at    = models.DateTimeField(auto_now_add=True)
    expires_at    = models.DateTimeField(null=True, blank=True,
                                         help_text='Optional: role expiry for temporary access')
    is_active     = models.BooleanField(default=True)

    class Meta:
        db_table        = 'rbac_user_role'
        unique_together = [('user', 'role', 'section', 'document_type')]
        ordering        = ['user', 'role']

    def __str__(self):
        scope = ''
        if self.section:
            scope += f' [section={self.section}]'
        if self.document_type:
            scope += f' [doctype={self.document_type}]'
        return f"{self.user.username} → {self.role}{scope}"


class DocumentPermissionOverride(models.Model):
    """Object-level permission override for a specific document and user."""

    class OverrideType(models.TextChoices):
        GRANT = 'GRANT', 'Grant'
        DENY  = 'DENY',  'Deny'

    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='doc_permission_overrides'
    )
    document   = models.ForeignKey(
        Document, on_delete=models.CASCADE,
        related_name='permission_overrides'
    )
    permission = models.CharField(max_length=30, choices=Permission.choices)
    override   = models.CharField(max_length=10, choices=OverrideType.choices)
    reason     = models.TextField(blank=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='overrides_granted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table        = 'rbac_doc_override'
        unique_together = [('user', 'document', 'permission')]

    def __str__(self):
        return (
            f"{self.user.username} | {self.document.document_number} — "
            f"{self.override} {self.permission}"
        )
