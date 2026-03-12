"""Optional LDAP/AD authentication backend for LAN environments.

Requires:  pip install django-auth-ldap
Activate in settings:
    AUTHENTICATION_BACKENDS = [
        'apps.security.auth_backend.PLWLDAPBackend',
        'django.contrib.auth.backends.ModelBackend',   # fallback
    ]

Configure via environment / .env:
    LDAP_SERVER_URI  = ldap://192.168.1.10
    LDAP_BIND_DN     = CN=edms_svc,OU=ServiceAccounts,DC=plw,DC=local
    LDAP_BIND_PASS   = <secret>
    LDAP_USER_SEARCH_BASE = OU=Employees,DC=plw,DC=local
    LDAP_REQUIRE_GROUP    = CN=EDMS_Users,OU=Groups,DC=plw,DC=local
"""
import os
import logging

logger = logging.getLogger(__name__)


class PLWLDAPBackend:
    """Thin wrapper — delegates to django-auth-ldap LDAPBackend."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            import ldap                            # noqa: F401
            from django_auth_ldap.backend import LDAPBackend
        except ImportError:
            logger.warning(
                'PLWLDAPBackend: django-auth-ldap not installed. '
                'Falling back to model backend.'
            )
            return None

        backend = LDAPBackend()
        return backend.authenticate(request, username=username, password=password)

    def get_user(self, user_id):
        try:
            from django_auth_ldap.backend import LDAPBackend
            return LDAPBackend().get_user(user_id)
        except Exception:  # noqa: BLE001
            return None
