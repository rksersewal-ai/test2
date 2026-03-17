# =============================================================================
# FILE: config/settings/production.py
# Hardened production settings for reverse-proxy HTTPS deployment.
# =============================================================================
"""Production settings - PLW EDMS + LDO. LAN-only deployment."""
from django.core.exceptions import ImproperlyConfigured
from decouple import config

from .base import *  # noqa


def _split_csv(name: str, *, default: str = '', required: bool = False) -> list[str]:
    value = config(name, default=default)
    items = [item.strip() for item in value.split(',') if item.strip()]
    if required and not items:
        raise ImproperlyConfigured(f'{name} must be set for production.')
    return items


DEBUG = False
SECRET_KEY = config('SECRET_KEY')

ALLOWED_HOSTS = _split_csv('ALLOWED_HOSTS', required=True)
CORS_ALLOWED_ORIGINS = _split_csv('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = _split_csv('CSRF_TRUSTED_ORIGINS')
CORS_ALLOW_CREDENTIALS = True

# Reverse-proxy / HTTPS hardening
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = config('USE_X_FORWARDED_HOST', cast=bool, default=True)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', cast=bool, default=True)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', cast=bool, default=True)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', cast=bool, default=True)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', cast=int, default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    'SECURE_HSTS_INCLUDE_SUBDOMAINS',
    cast=bool,
    default=True,
)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', cast=bool, default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# Explicit production infra dependencies
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)

# Ensure runtime directories exist before logging/static/media initialization.
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
STATIC_ROOT.mkdir(parents=True, exist_ok=True)
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
Path(OCR_WATCH_FOLDER).mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class':       'logging.handlers.RotatingFileHandler',
            'filename':    str(LOG_DIR / 'edms.log'),
            'maxBytes':    10485760,
            'backupCount': 10,
            'formatter':   'verbose',
        },
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level':    'INFO',
    },
    'loggers': {
        'scanner': {'level': 'INFO', 'propagate': True},
        'webhooks': {'level': 'INFO', 'propagate': True},
        'sharelinks': {'level': 'INFO', 'propagate': True},
    },
}
