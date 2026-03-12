"""LAN-only security middleware - blocks requests from outside allowed IP ranges."""
import ipaddress
import logging
from django.http import HttpResponseForbidden
from django.conf import settings

logger = logging.getLogger(__name__)


class LanOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._load_ranges()

    def _load_ranges(self):
        self.allowed_ranges = []
        if getattr(settings, 'DISABLE_LAN_RESTRICTION', False):
            return
        for cidr in getattr(settings, 'ALLOWED_IP_RANGES', []):
            try:
                self.allowed_ranges.append(ipaddress.ip_network(cidr.strip(), strict=False))
            except ValueError:
                logger.warning(f'Invalid IP range in ALLOWED_IP_RANGES: {cidr}')

    def __call__(self, request):
        if self.allowed_ranges:
            client_ip = self._get_ip(request)
            try:
                addr = ipaddress.ip_address(client_ip)
                if not any(addr in net for net in self.allowed_ranges):
                    logger.warning(f'Blocked request from outside LAN: {client_ip}')
                    return HttpResponseForbidden('Access restricted to internal network.')
            except ValueError:
                return HttpResponseForbidden('Invalid client IP.')
        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
