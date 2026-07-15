@echo off
chcp 65001 >nul
echo ========================================
echo   TCA Proxy Server - Local Proxy Server
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [START] Starting proxy server...
echo [URL] http://127.0.0.1:8081
echo.
echo [TIP] Press Ctrl+C to stop
echo.

python -m src.server.proxy

pause
