r"""Windows production WSGI server using Waitress.

Usage (from project root):
    python deployment/waitress_server.py

Run as Windows Service via NSSM:
    nssm install PLW-EDMS "C:\Python311\python.exe" "D:\plw_edms\deployment\waitress_server.py"
    nssm set PLW-EDMS AppDirectory D:\plw_edms
    nssm set PLW-EDMS AppEnvironmentExtra DJANGO_SETTINGS_MODULE=config.settings.production
    nssm start PLW-EDMS
"""
import os
import sys
import logging

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'waitress.log')),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger('waitress')


def main():
    from decouple import config
    from waitress import serve
    from django.core.wsgi import get_wsgi_application

    host = config('WAITRESS_HOST', default='127.0.0.1')
    port = config('WAITRESS_PORT', default=8000, cast=int)
    threads = config('WAITRESS_THREADS', default=8, cast=int)

    application = get_wsgi_application()

    logger.info('PLW EDMS starting on http://%s:%s  (threads=%s)', host, port, threads)
    serve(
        application,
        host=host,
        port=port,
        threads=threads,
        channel_timeout=120,
        cleanup_interval=30,
        connection_limit=200,
    )


if __name__ == '__main__':
    main()
