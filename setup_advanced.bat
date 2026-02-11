@echo off
chcp 65001 > nul
title Setup Advanced Crawler (Scrapy)

echo ========================================
echo  Advanced Crawler Setup (Scrapy)
echo ========================================
echo.
echo This will install Scrapy and Playwright
echo for crawling React/Vue/SPA websites.
echo.
echo Installation size: ~150MB
echo Installation time: ~5-10 minutes
echo.
pause

echo.
echo [1/2] Installing Python packages...
pip install scrapy scrapy-playwright readability-lxml

if errorlevel 1 (
    echo [ERROR] Package installation failed
    pause
    exit /b 1
)

echo.
echo [2/2] Installing Playwright browser (Chromium)...
echo This will download ~100MB...
playwright install chromium

if errorlevel 1 (
    echo [ERROR] Playwright installation failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo You can now use the Advanced Crawler
echo in the launcher GUI.
echo.
pause
