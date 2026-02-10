@echo off
chcp 65001 > nul
title Doxygen 크롤러

echo ========================================
echo  Doxygen 문서 크롤러
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다.
    echo Python 3.8 이상을 설치하세요: https://www.python.org
    pause
    exit /b 1
)

REM Install packages
echo 패키지 설치 중...
pip install requests beautifulsoup4 pypdf --quiet 2>nul
if errorlevel 1 (
    echo [경고] 일부 패키지 설치 실패 (계속 진행)
)
echo 패키지: OK
echo.

REM Run GUI
echo GUI 실행 중...
echo.
python gui.py

if errorlevel 1 (
    echo.
    echo [오류] 실행 실패
    pause
)
