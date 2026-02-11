@echo off
chcp 65001 > nul
title Unified Web Crawler

echo ========================================
echo  Unified Web Crawler
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.8+: https://www.python.org
    pause
    exit /b 1
)

REM Install basic packages (for simple crawler)
echo Installing basic packages...
pip install requests beautifulsoup4 pypdf --quiet 2>nul

echo.
echo Starting launcher...
echo.

REM Run with error display
python launcher.py

REM Always pause to see errors
echo.
echo ========================================
if errorlevel 1 (
    echo [ERROR] Execution failed - see error above
) else (
    echo Program closed
)
echo ========================================
pause
