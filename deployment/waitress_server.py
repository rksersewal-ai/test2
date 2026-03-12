"""waitress WSGI server entry point for Windows LAN deployment.
Run: python deployment/waitress_server.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

from waitress import serve
from config.wsgi import application

if __name__ == '__main__':
    print('Starting PLW EDMS on http://0.0.0.0:8000')
    serve(application, host='0.0.0.0', port=8000, threads=8, connection_limit=100)
