# =============================================================================
# FILE: config/settings/production.py
# FIXED: Celery broker/backend must be explicitly set in production env
# =============================================================================
"""Production settings - PLW EDMS + LDO. LAN-only deployment."""
from .base import *  # noqa
from decouple import config

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

CORS_ALLOWED_ORIGINS   = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True

# Security headers for LAN HTTPS
SECURE_SSL_REDIRECT            = False   # Handled by nginx reverse proxy
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SECURE_HSTS_SECONDS            = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = 'DENY'

# FIX #12: Celery overrides for production — inherit from base but
# ensure broker URL is sourced from env (not fallback default)
CELERY_BROKER_URL     = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')

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
            'filename':    'logs/edms.log',
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
