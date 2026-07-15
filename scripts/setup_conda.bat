@echo off
REM ============================================================
REM YEAN — Terminal Coding Agent 环境初始化脚本 (Windows)
REM 在 data_analysis conda 环境下部署
REM ============================================================

setlocal enabledelayedexpansion

set "CONDA_ENV=data_analysis"
set "CONDA_ROOT=D:\Anaconda"
set "CONDA_BAT=%CONDA_ROOT%\condabin\conda.bat"

if not exist "%CONDA_BAT%" (
    echo [错误] 找不到 conda.bat: %CONDA_BAT%
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   YEAN — 环境初始化
echo   Conda 环境: %CONDA_ENV%
echo ============================================================
echo.

REM 激活 conda
call "%CONDA_BAT%" activate "%CONDA_ENV%" 2>nul
if errorlevel 1 (
    echo [错误] 无法激活 conda 环境: %CONDA_ENV%
    echo 请先运行: conda create -n %CONDA_ENV% python=3.10
    pause
    exit /b 1
)

REM 升级 pip
echo [1/4] 升级 pip...
pip install --upgrade pip

REM 安装依赖
echo [2/4] 安装依赖...
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM 安装项目（可编辑模式）
echo [3/4] 安装 YEAN（可编辑模式）...
pip install -e .

REM 配置 .env
if not exist ".env" (
    echo [4/4] 创建 .env 文件...
    copy /y .env.example .env >nul
    echo 请编辑 .env 文件，填入你的 API Key
) else (
    echo [4/4] .env 已存在，跳过
)

echo.
echo ============================================================
echo   ✅ 环境初始化完成！
echo.
echo   下一步：
echo     1. 编辑 .env 文件，填入 API Key
echo     2. 运行 scripts\start_yeanc.bat 启动 YEAN
echo     3. 或运行: yean
echo ============================================================
echo.

endlocal
