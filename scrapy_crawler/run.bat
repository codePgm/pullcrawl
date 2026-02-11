@echo off
chcp 65001 > nul
title Scrapy 크롤러 실행

echo ========================================
echo  Scrapy 크롤러 실행
echo ========================================
echo.

REM Default parameters
set URL=https://example.com
set DOMAIN=example.com
set MAX_PAGES=100
set OUTPUT=./output

REM Check if parameters provided
if not "%~1"=="" set URL=%~1
if not "%~2"=="" set DOMAIN=%~2
if not "%~3"=="" set MAX_PAGES=%~3

echo URL: %URL%
echo 도메인: %DOMAIN%
echo 최대 페이지: %MAX_PAGES%
echo 출력 폴더: %OUTPUT%
echo.
echo 크롤링 시작...
echo.

scrapy crawl site -a seed="%URL%" -a allowed_domains="%DOMAIN%" -a out_dir="%OUTPUT%" -a max_pages=%MAX_PAGES% -a max_depth=4

echo.
echo ========================================
echo 크롤링 완료!
echo 결과: %OUTPUT%\pages.jsonl
echo ========================================
pause
