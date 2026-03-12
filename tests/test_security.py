"""Security middleware tests — PRD Section 21."""
import pytest
from django.test import RequestFactory, override_settings
from apps.security.middleware import (
    LANOnlyMiddleware, SecurityHeadersMiddleware, AuditRequestMiddleware
)
from django.http import HttpResponse


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
