# EDMS-LDO — Port Reference

This document is the single source of truth for all network ports used by the EDMS-LDO application.

## Assigned Ports

| Service | Port | Protocol | Notes |
|---|---|---|---|
| **Django Backend** | **8765** | HTTP | All API calls, Admin, Media files |
| **Vite Frontend (dev)** | **4173** | HTTP | Dev server + built preview |
| **PostgreSQL** | 5432 | TCP | Local DB (default) |
| **Redis** *(optional)* | 6379 | TCP | Celery broker for OCR jobs |

## Ports Reserved / Avoided

| Port | Occupied By | Reason Avoided |
|---|---|---|
| 8000 | **DSC Signer** (office PCs) | Conflicts with digital signature service |
| 80 | HTTP / IIS | OS-level, needs admin |
| 443 | HTTPS / IIS | OS-level, needs admin |
| 8080 | Tomcat / web proxies | Too common, often blocked |
| 3000 | Various JS dev servers | Commonly occupied |
| 5173 | Vite default | Can clash on shared dev machines |
| 3306 | MySQL | Reserved |
| 9000 | SonarQube / PHP-FPM | Risk on shared servers |

## Start Commands

```bash
# Backend (from /backend directory)
python manage.py runserver 0.0.0.0:8765

# Frontend dev (from /frontend directory)
npm run dev
# Vite reads port 4173 from vite.config.ts automatically

# Access from LAN clients
http://<server-IP>:4173        # frontend UI
http://<server-IP>:8765/admin  # Django admin
http://<server-IP>:8765/api/v1/ # REST API
```

## Windows Firewall Rules (run as Administrator)

```cmd
netsh advfirewall firewall add rule name="EDMS Backend" dir=in action=allow protocol=TCP localport=8765
netsh advfirewall firewall add rule name="EDMS Frontend" dir=in action=allow protocol=TCP localport=4173
```

## Verify Ports Are Free (Before Starting)

```cmd
netstat -ano | findstr :8765
netstat -ano | findstr :4173
```
If output is empty — ports are free and safe to use.
