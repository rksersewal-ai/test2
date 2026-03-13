"""Security middleware tests — PRD Section 21."""
import pytest
import sys
from unittest import mock
from django.test import RequestFactory, override_settings
from apps.security.middleware import (
    LANOnlyMiddleware, SecurityHeadersMiddleware, AuditRequestMiddleware
)
from apps.security.auth_backend import PLWLDAPBackend
from django.http import HttpResponse


class TestPLWLDAPBackend:
    @mock.patch.dict('sys.modules', {'ldap': None, 'django_auth_ldap': None, 'django_auth_ldap.backend': None})
    def test_authenticate_without_ldap(self, caplog):
        backend = PLWLDAPBackend()
        result = backend.authenticate(None, username='test', password='password')
        assert result is None
        assert 'PLWLDAPBackend: django-auth-ldap not installed' in caplog.text

    @mock.patch.dict('sys.modules', {'django_auth_ldap': None, 'django_auth_ldap.backend': None})
    def test_get_user_without_ldap(self):
        backend = PLWLDAPBackend()
        result = backend.get_user(1)
        assert result is None

    @mock.patch.dict('sys.modules')
    def test_authenticate_with_ldap(self):
        mock_ldap = mock.MagicMock()
        mock_django_auth_ldap = mock.MagicMock()
        mock_django_auth_ldap_backend = mock.MagicMock()

        mock_ldap_backend_class = mock.MagicMock()
        mock_ldap_backend_instance = mock.MagicMock()
        mock_ldap_backend_class.return_value = mock_ldap_backend_instance
        mock_django_auth_ldap_backend.LDAPBackend = mock_ldap_backend_class

        mock_user = mock.MagicMock()
        mock_ldap_backend_instance.authenticate.return_value = mock_user

        sys.modules['ldap'] = mock_ldap
        sys.modules['django_auth_ldap'] = mock_django_auth_ldap
        sys.modules['django_auth_ldap.backend'] = mock_django_auth_ldap_backend

        backend = PLWLDAPBackend()
        result = backend.authenticate(None, username='test', password='password')

        assert result == mock_user
        mock_ldap_backend_instance.authenticate.assert_called_once_with(None, username='test', password='password')

    @mock.patch.dict('sys.modules')
    def test_get_user_with_ldap(self):
        mock_django_auth_ldap = mock.MagicMock()
        mock_django_auth_ldap_backend = mock.MagicMock()

        mock_ldap_backend_class = mock.MagicMock()
        mock_ldap_backend_instance = mock.MagicMock()
        mock_ldap_backend_class.return_value = mock_ldap_backend_instance
        mock_django_auth_ldap_backend.LDAPBackend = mock_ldap_backend_class

        mock_user = mock.MagicMock()
        mock_ldap_backend_instance.get_user.return_value = mock_user

        sys.modules['django_auth_ldap'] = mock_django_auth_ldap
        sys.modules['django_auth_ldap.backend'] = mock_django_auth_ldap_backend

        backend = PLWLDAPBackend()
        result = backend.get_user(1)

        assert result == mock_user
        mock_ldap_backend_instance.get_user.assert_called_once_with(1)


class TestSecurityHeadersMiddleware:
    def _get_response(self, request):
        return HttpResponse('ok')

    def test_headers_present(self):
        factory = RequestFactory()
        request = factory.get('/')
        mw = SecurityHeadersMiddleware(self._get_response)
        response = mw(request)
        assert response['X-Content-Type-Options'] == 'nosniff'
        assert response['X-Frame-Options'] == 'SAMEORIGIN'
        assert 'Content-Security-Policy' in response
        assert response['Cache-Control'] == 'no-store'


class TestLANOnlyMiddleware:
    def _get_response(self, request):
        return HttpResponse('ok')

    @override_settings(DEBUG=False, ALLOWED_LAN_NETWORKS=['192.168.1.0/24'])
    def test_lan_ip_allowed(self):
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/', REMOTE_ADDR='192.168.1.50')
        mw = LANOnlyMiddleware(self._get_response)
        response = mw(request)
        assert response.status_code == 200

    @override_settings(DEBUG=False, ALLOWED_LAN_NETWORKS=['192.168.1.0/24'])
    def test_external_ip_blocked(self):
        factory = RequestFactory()
        request = factory.get('/', REMOTE_ADDR='8.8.8.8')
        mw = LANOnlyMiddleware(self._get_response)
        response = mw(request)
        assert response.status_code == 403

    @override_settings(DEBUG=True)
    def test_debug_mode_bypasses_lan_check(self):
        factory = RequestFactory()
        request = factory.get('/', REMOTE_ADDR='8.8.8.8')
        mw = LANOnlyMiddleware(self._get_response)
        response = mw(request)
        assert response.status_code == 200  # debug mode: no block
