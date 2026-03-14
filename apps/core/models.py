# =============================================================================
# FILE: apps/core/models.py
# SPRINT 8 UPDATE: Added TOTP fields to User model.
# All existing fields preserved exactly.
# =============================================================================
"""Core models: User, Section, Role - PLW EDMS + LDO."""
import secrets
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Section(models.Model):
    code        = models.CharField(max_length=20, unique=True)
    name        = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    parent      = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children'
    )
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'core_section'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.name}'


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN        = 'ADMIN',        'Administrator'
        SECTION_HEAD = 'SECTION_HEAD', 'Section Head'
        ENGINEER     = 'ENGINEER',     'Engineer'
        LDO_STAFF    = 'LDO_STAFF',    'LDO Staff'
        AUDIT        = 'AUDIT',        'Audit'
        VIEWER       = 'VIEWER',       'Viewer'

    username        = models.CharField(max_length=60, unique=True)
    email           = models.EmailField(blank=True)
    full_name       = models.CharField(max_length=150)
    employee_code   = models.CharField(max_length=30, unique=True, null=True, blank=True)
    designation     = models.CharField(max_length=100, blank=True)
    section         = models.ForeignKey(
        Section, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='users'
    )
    role            = models.CharField(
        max_length=20, choices=Role.choices, default=Role.VIEWER
    )
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    last_login_ip   = models.GenericIPAddressField(null=True, blank=True)

    # -------------------------------------------------------------------------
    # SPRINT 8: TOTP / 2FA fields
    # -------------------------------------------------------------------------
    totp_secret     = models.CharField(
        max_length=64, blank=True,
        help_text='Base32-encoded TOTP secret. Empty = 2FA not set up.'
    )
    totp_enabled    = models.BooleanField(
        default=False,
        help_text='True after user has verified first TOTP code post-setup.'
    )
    totp_backup_codes = models.JSONField(
        default=list,
        help_text='List of hashed one-time backup codes (8 codes, shown once at setup).'
    )
    totp_enforced_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Timestamp when admin forced 2FA on this account.'
    )

    objects = UserManager()

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'core_user'
        ordering = ['username']

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_audit_user(self):
        return self.role == self.Role.AUDIT

    # ---- TOTP helpers -------------------------------------------------------

    def generate_backup_codes(self) -> list[str]:
        """
        Generate 8 plaintext backup codes (shown once to user),
        store their SHA-256 hashes, return plaintext list.
        """
        import hashlib
        codes   = [secrets.token_hex(5).upper() for _ in range(8)]  # e.g. 'A3F8C2'
        hashes  = [hashlib.sha256(c.encode()).hexdigest() for c in codes]
        self.totp_backup_codes = hashes
        self.save(update_fields=['totp_backup_codes'])
        return codes

    def consume_backup_code(self, code: str) -> bool:
        """
        Verify and consume a backup code (one-time use).
        Returns True if valid; removes the used hash.
        """
        import hashlib
        h = hashlib.sha256(code.strip().upper().encode()).hexdigest()
        if h in self.totp_backup_codes:
            remaining = [x for x in self.totp_backup_codes if x != h]
            self.totp_backup_codes = remaining
            self.save(update_fields=['totp_backup_codes'])
            return True
        return False
