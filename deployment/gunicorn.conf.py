# Gunicorn configuration - PLW EDMS production
# Run: gunicorn -c deployment/gunicorn.conf.py config.wsgi:application

import multiprocessing

# Binding
bind = '127.0.0.1:8000'

# Workers (2 × CPU cores + 1 for IO-bound Django)
workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = 'sync'
worker_connections = 100
threads = 2
timeout = 120
keepalive = 5

# Logging
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%({X-Real-IP}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"'

# Process naming
proc_name = 'edms_gunicorn'

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Graceful restart
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# PID file
pidfile = '/tmp/edms_gunicorn.pid'
