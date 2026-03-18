# =============================================================================
# FILE: config/waitress_config.py
#
# Waitress WSGI server configuration for PLW EDMS LAN deployment.
#
# USAGE:
#   python config/waitress_config.py
#
# Or via serve() in your start script:
#   from config.waitress_config import serve_app
#   serve_app()
#
# TUNING RATIONALE (LAN, ~20-50 concurrent users, Windows Server):
#   threads=16:
#     Each thread handles one request at a time. With 16 threads:
#     - 16 simultaneous API calls handled without queuing
#     - Matches CONN_MAX_AGE=60 pool — each thread gets 1 DB connection
#     - Stays well within typical Windows Server open-file limits
#     - CPU: Django is I/O-bound (DB + disk), not CPU-bound — 16 threads
#       utilises multiple cores without thrashing
#
#   channel_timeout=120:
#     Large PDF uploads (50 MB) on a LAN at 100 Mbps take ~4 seconds.
#     120s allows headroom for OCR-bound operations without killing connections.
#
#   max_request_body_size=104857600 (100 MB):
#     Matches FILE_UPLOAD_MAX_MEMORY_SIZE in settings. Prevents Waitress from
#     accepting bodies Django will reject anyway.
#
#   connection_limit=200:
#     Max open TCP connections. On a /24 LAN with 50 users, each user may have
#     2-4 open connections (browser parallelism). 200 gives 4x headroom.
#
#   cleanup_interval=30:
#     Closes idle connections every 30s, freeing OS sockets faster during
#     peak-then-idle patterns (end of shift usage spike).
# =============================================================================
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')


def serve_app():
    """Start the Waitress WSGI server with production-tuned settings."""
    try:
        from waitress import serve
    except ImportError:
        print('[ERROR] waitress is not installed. Run: pip install waitress')
        sys.exit(1)

    import django
    django.setup()
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

    host   = os.environ.get('WAITRESS_HOST', '0.0.0.0')
    port   = int(os.environ.get('WAITRESS_PORT', '8000'))

    print(f'[EDMS] Starting Waitress on {host}:{port} with 16 threads...')

    serve(
        application,
        host                  = host,
        port                  = port,
        threads               = 16,          # See tuning rationale above
        channel_timeout       = 120,         # seconds before idle channel closed
        max_request_body_size = 104857600,   # 100 MB hard cap
        connection_limit      = 200,         # max simultaneous TCP connections
        cleanup_interval      = 30,          # close idle channels every 30s
        ident                 = None,        # hide server identity from HTTP headers
        asyncore_use_poll     = True,        # better performance on Windows
    )


if __name__ == '__main__':
    serve_app()
