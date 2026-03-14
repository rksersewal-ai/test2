#!/bin/bash
# =============================================================================
# FILE: nginx/gunicorn_start.sh
# Start Gunicorn for EDMS-LDO in production (Linux / WSL)
# Usage: bash nginx/gunicorn_start.sh
# Or register as a systemd service (see below)
# =============================================================================

set -e

PROJECT_DIR="/opt/edms/backend"
VENV_DIR="$PROJECT_DIR/venv"
GUNICORN="$VENV_DIR/bin/gunicorn"
BIND="127.0.0.1:8765"
WORKERS=3          # (2 x CPU cores) + 1 — adjust for your server
TIMEOUT=120
LOG_DIR="/opt/edms/logs"

mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"

exec "$GUNICORN" edms.wsgi:application \
    --bind        "$BIND"              \
    --workers     "$WORKERS"           \
    --timeout     "$TIMEOUT"           \
    --access-logfile "$LOG_DIR/access.log" \
    --error-logfile  "$LOG_DIR/error.log"  \
    --log-level   info                 \
    --preload
