@echo off
REM =============================================================================
REM FILE: deployment/generate_ssl_cert.bat
REM Generates a self-signed SSL certificate for LAN HTTPS deployment.
REM Requires: OpenSSL installed (bundled with Git for Windows at C:\Program Files\Git\usr\bin)
REM
REM Output:
 REM   C:\nginx\ssl\edms.crt   (certificate)
REM   C:\nginx\ssl\edms.key   (private key)
REM =============================================================================

setlocal

set OPENSSL=openssl
set SSL_DIR=C:\nginx\ssl
set SERVER_IP=192.168.1.100
set SERVER_NAME=edms.lan

REM Try Git-bundled openssl if not in PATH
if not exist "%OPENSSL%" (
    set OPENSSL=C:\Program Files\Git\usr\bin\openssl.exe
)

echo Creating SSL directory at %SSL_DIR%...
if not exist "%SSL_DIR%" mkdir "%SSL_DIR%"

echo Generating 4096-bit RSA self-signed cert valid 10 years...
echo (Common Name = %SERVER_NAME%, SAN = %SERVER_IP%)
echo.

REM Create openssl config with Subject Alternative Names (SAN) for both IP and hostname
(
echo [req]
echo default_bits = 4096
echo prompt = no
echo default_md = sha256
echo distinguished_name = dn
echo x509_extensions = v3_req
echo.
echo [dn]
echo C = IN
echo ST = Punjab
echo L = Patiala
echo O = Patiala Locomotive Works
echo OU = IT
echo CN = %SERVER_NAME%
echo.
echo [v3_req]
echo subjectAltName = @alt_names
echo basicConstraints = CA:FALSE
echo keyUsage = nonRepudiation, digitalSignature, keyEncipherment
echo.
echo [alt_names]
echo DNS.1 = %SERVER_NAME%
echo DNS.2 = localhost
echo IP.1  = %SERVER_IP%
echo IP.2  = 127.0.0.1
) > "%TEMP%\edms_ssl.cnf"

"%OPENSSL%" req -x509 -newkey rsa:4096 ^
    -keyout "%SSL_DIR%\edms.key" ^
    -out    "%SSL_DIR%\edms.crt" ^
    -days 3650 -nodes ^
    -config "%TEMP%\edms_ssl.cnf"

if errorlevel 1 (
    echo.
    echo [ERROR] OpenSSL not found or certificate generation failed.
    echo         Install Git for Windows (includes OpenSSL) or standalone OpenSSL.
    echo         https://slproweb.com/products/Win32OpenSSL.html
    pause & exit /b 1
)

del "%TEMP%\edms_ssl.cnf"

echo.
echo [OK] Certificate generated:
echo      %SSL_DIR%\edms.crt
echo      %SSL_DIR%\edms.key
echo.
echo NOTE: Browsers will show a security warning because this is self-signed.
echo       To suppress warnings on office PCs, install edms.crt as a
echo       Trusted Root Certificate via: certmgr.msc
pause
