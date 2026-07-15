@echo off
REM ============================================================
REM YEAN — Terminal Coding Agent 启动器
REM 在 data_analysis conda 环境下运行
REM ============================================================

setlocal enabledelayedexpansion

REM ── 配置 ──
set "CONDA_ENV=data_analysis"
set "CONDA_ROOT=D:\Anaconda"

REM ── 定位 conda.bat ──
set "CONDA_BAT=%CONDA_ROOT%\condabin\conda.bat"
if not exist "%CONDA_BAT%" (
    echo [错误] 找不到 conda.bat: %CONDA_BAT%
    echo 请检查 CONDA_ROOT 路径是否正确。
    pause
    exit /b 1
)

REM ── 激活 conda 环境 ──
call "%CONDA_BAT%" activate "%CONDA_ENV%" 2>nul
if errorlevel 1 (
    echo [错误] 无法激活 conda 环境: %CONDA_ENV%
    echo 请先运行: conda create -n %CONDA_ENV% python=3.10
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   YEAN — Terminal Coding Agent
echo   环境: %CONDA_ENV%
echo   Python: %CONDA_PREFIX%
echo ============================================================
echo.

REM ── 启动 YEAN ──
REM 如果传了参数，作为单次执行；否则进入交互模式
if "%~1"=="" (
    yean
) else (
    yean %*
)

endlocal
