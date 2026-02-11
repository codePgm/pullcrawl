@echo off
chcp 65001 > nul
title Scrapy 크롤러 설치

echo ========================================
echo  Scrapy 크롤러 설치
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

echo [1/3] Python 패키지 설치 중...
pip install scrapy scrapy-playwright readability-lxml

if errorlevel 1 (
    echo [오류] 패키지 설치 실패
    pause
    exit /b 1
)

echo.
echo [2/3] Playwright 브라우저 설치 중...
echo (Chrome 브라우저 다운로드 - 약 100MB, 시간이 걸립니다)
playwright install chromium

if errorlevel 1 (
    echo [오류] Playwright 설치 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo  ✅ 설치 완료!
echo ========================================
echo.
echo 이제 run.bat을 실행하여 크롤링을 시작하세요.
echo.
pause
