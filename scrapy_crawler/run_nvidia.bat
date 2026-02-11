@echo off
chcp 65001 > nul
title NVIDIA 문서 크롤링

echo ========================================
echo  NVIDIA DRIVE OS 문서 크롤링
echo ========================================
echo.

set URL=https://developer.nvidia.com/docs/drive/drive-os/6.0.10/public/drive-os-linux-sdk/api_reference/index.html
set DOMAIN=developer.nvidia.com
set MAX_PAGES=500
set OUTPUT=./nvidia_docs

echo URL: %URL%
echo 도메인: %DOMAIN%
echo 최대 페이지: %MAX_PAGES%
echo 출력: %OUTPUT%
echo.
echo ⚠️  경고: 이 크롤링은 시간이 오래 걸립니다 (약 30-60분)
echo.
pause

echo.
echo 크롤링 시작...
echo.

scrapy crawl site ^
  -a seed="%URL%" ^
  -a allowed_domains="%DOMAIN%" ^
  -a out_dir="%OUTPUT%" ^
  -a max_pages=%MAX_PAGES% ^
  -a max_depth=4 ^
  -a render=0

echo.
echo ========================================
echo 완료!
echo 결과: %OUTPUT%\pages.jsonl
echo ========================================
pause
