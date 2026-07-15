@echo off
chcp 65001 >nul
echo ========================================
echo   TCA Proxy - Local Proxy Config Tool
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [START] Launching config GUI...
python -m src.gui.proxy_gui

pause
