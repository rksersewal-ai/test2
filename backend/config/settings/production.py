"""
PLW EDMS — Production Settings
"""
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_SSL_REDIRECT = False  # Handled at reverse proxy

DATABASES['default']['CONN_MAX_AGE'] = 600

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'plw-edms-cache',
    }
}

# Suppress console logging in production
LOGGING['handlers']['console']['level'] = 'WARNING'
