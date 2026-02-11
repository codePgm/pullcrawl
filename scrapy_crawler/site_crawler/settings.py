import asyncio
import os

BOT_NAME = "site_crawler"

SPIDER_MODULES = ["site_crawler.spiders"]
NEWSPIDER_MODULE = "site_crawler.spiders"

ROBOTSTXT_OBEY = True

# 동시성 (HTTP)
CONCURRENT_REQUESTS = 16
DOWNLOAD_TIMEOUT = 30
RETRY_ENABLED = True
RETRY_TIMES = 3

# 호스트별 폴리트니스
DOWNLOAD_DELAY = 0.25
RANDOMIZE_DOWNLOAD_DELAY = True

# 기본 헤더
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en,ko;q=0.9",
}

# DupeFilter(요청 단위) 기본
DUPEFILTER_CLASS = "scrapy.dupefilters.RFPDupeFilter"

# 파이프라인: 이미지 다운로드 + JSONL 저장
ITEM_PIPELINES = {
    # "site_crawler.pipelines.ImageAndJsonlPipeline": 300,
    "site_crawler.pipelines.JsonlPipeline": 300,
}

# Media(이미지) 설정: 파이프라인에서 out_dir 하위로 저장 경로를 동적으로 잡습니다.
IMAGES_STORE = os.path.abspath(os.getenv("CRAWL_OUT_DIR", "./dump"))

# scrapy-playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30_000

# 브라우저 동시성 제한 (중요)
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4

# 필요 시 프록시/헤더 등은 context kwargs로 설정 가능

LOG_LEVEL = "INFO"

# Auto-close when idle (크롤링 완료 시 자동 종료)
# 60초간 새 요청이 없으면 자동으로 종료
CLOSESPIDER_TIMEOUT = 120  # 2분간 idle 시 종료
CLOSESPIDER_ERRORCOUNT = 50  # 에러 50개 발생 시 종료 (안전장치)
