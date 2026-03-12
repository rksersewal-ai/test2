# Windows IIS + wfastcgi Setup Guide for PLW EDMS

## Option A: Recommended — nginx + gunicorn on Windows

Install nginx for Windows and run gunicorn via a Windows Service.
This avoids IIS Python CGI complexity.

### Step 1: Install dependencies
```
pip install -r requirements.txt
pip install gunicorn  # works on Windows via waitress fallback
```

### Step 2: Use waitress as WSGI server (Windows-native)
```
pip install waitress
waitress-serve --listen=127.0.0.1:8000 config.wsgi:application
```

### Step 3: Create a Windows Service with NSSM
```
nssm install EDMS-Backend "C:\EDMS\venv\Scripts\waitress-serve.exe"
nssm set EDMS-Backend AppParameters --listen=127.0.0.1:8000 config.wsgi:application
nssm set EDMS-Backend AppDirectory C:\EDMS
nssm set EDMS-Backend AppEnvironmentExtra DJANGO_SETTINGS_MODULE=config.settings.production
nssm start EDMS-Backend
```

### Step 4: nginx as reverse proxy
Copy `deployment/nginx.conf` to `C:\nginx\conf\nginx.conf`
Adjust `ssl_certificate` paths to Windows paths.
Run nginx as a Windows Service:
```
nssm install nginx C:\nginx\nginx.exe
nssm start nginx
```

## Option B: IIS with wfastcgi (Advanced)

1. Enable IIS + CGI feature in Windows Features
2. Install wfastcgi: `pip install wfastcgi` then `wfastcgi-enable`
3. Create IIS site pointing to project root
4. Set web.config (see below)
5. Set WSGI_HANDLER = config.wsgi.application

### web.config for IIS + wfastcgi
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="Python FastCGI"
           path="*"
           verb="*"
           modules="FastCgiModule"
           scriptProcessor="C:\EDMS\venv\Scripts\python.exe|C:\EDMS\venv\Lib\site-packages\wfastcgi.py"
           resourceType="Unspecified"
           requireAccess="Script" />
    </handlers>
  </system.webServer>
  <appSettings>
    <add key="WSGI_HANDLER" value="config.wsgi.application" />
    <add key="PYTHONPATH" value="C:\EDMS" />
    <add key="DJANGO_SETTINGS_MODULE" value="config.settings.production" />
  </appSettings>
</configuration>
```

## PostgreSQL Windows Service
```
# Verify service running
Get-Service -Name postgresql*
# Test connection
psql -U edms_user -d edms_ldo -h localhost
```

## SSL Certificate (Self-signed for LAN)
```bash
openssl req -x509 -newkey rsa:4096 -keyout edms.key -out edms.crt -days 3650 -nodes \
  -subj "/CN=edms.lan/O=PLW/C=IN"
```
