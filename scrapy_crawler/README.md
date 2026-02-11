# 🕷️ Scrapy 크롤러 (Site Crawler for LLM)

강력한 웹 크롤러 - Scrapy + Playwright 기반

## ✨ 특징

- ✅ **Playwright 렌더링** - React/Vue/Angular 등 SPA 지원
- ✅ **CSS 배경 이미지** - computed style에서 추출
- ✅ **본문 추출** - readability-lxml 사용
- ✅ **이미지 다운로드** - 자동 저장 (선택 사항)
- ✅ **깊이 제어** - 링크 탐색 깊이 설정
- ✅ **JSONL 출력** - 구조화된 데이터

## 📁 프로젝트 구조

```
scrapy_setup/
├── site_crawler/              # 메인 프로젝트
│   ├── spiders/
│   │   ├── __init__.py
│   │   └── site_spider.py    # 크롤링 로직
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── cssbg.py          # CSS 배경 추출
│   │   ├── text.py           # 텍스트 추출
│   │   └── urlnorm.py        # URL 정규화
│   ├── __init__.py
│   ├── items.py              # 데이터 구조
│   ├── middlewares.py
│   ├── pipelines.py          # 저장 로직
│   └── settings.py           # 설정
│
├── scrapy.cfg                # Scrapy 설정
├── requirements.txt          # 패키지 목록
├── setup.bat                 # 설치 스크립트
├── run.bat                   # 실행 스크립트
├── run_nvidia.bat            # NVIDIA 문서용
└── README.md                 # 이 파일
```

## 🚀 빠른 시작

### 1단계: 설치

```bash
# Windows
setup.bat 더블클릭

# 수동 설치
pip install -r requirements.txt
playwright install chromium
```

**설치 시간:** 약 5-10분 (Chrome 브라우저 다운로드 포함)

### 2단계: 실행

#### 방법 1: 기본 실행 (GUI 없음)

```bash
run.bat
```

URL과 도메인을 입력하라고 나옵니다.

#### 방법 2: 명령줄 파라미터

```bash
# Windows
run.bat "https://example.com" "example.com" 100

# 직접 실행
scrapy crawl site -a seed="URL" -a allowed_domains="DOMAIN" -a max_pages=100
```

#### 방법 3: NVIDIA 문서 크롤링

```bash
run_nvidia.bat
```

## ⚙️ 파라미터 설명

| 파라미터 | 설명 | 기본값 | 예시 |
|----------|------|--------|------|
| `seed` | 시작 URL | 필수 | https://example.com |
| `allowed_domains` | 크롤링 허용 도메인 | 필수 | example.com |
| `out_dir` | 출력 폴더 | ./dump | ./output |
| `max_pages` | 최대 페이지 수 | 500 | 100 |
| `max_depth` | 최대 링크 깊이 | 4 | 3 |
| `render` | Playwright 사용 (0/1) | 1 | 0 |
| `include_css_bg` | CSS 배경 수집 (0/1) | 1 | 0 |

## 📊 출력 형식

### pages.jsonl

각 줄이 하나의 페이지 (JSONL 형식):

```json
{
  "url": "https://example.com/page1",
  "final_url": "https://example.com/page1",
  "fetched_at": "2024-02-10T12:00:00+00:00",
  "status": 200,
  "rendered": true,
  "title": "Page Title",
  "text": "Main content text extracted by readability...",
  "images": [
    {
      "type": "img",
      "src": "https://example.com/image.jpg",
      "alt": "Image description",
      "local_path": "images/example.com/abc123/img.jpg"
    }
  ],
  "out_links": ["https://example.com/page2"],
  "depth": 0,
  "page_key": "abc123def456"
}
```

## 🎯 사용 예시

### 예시 1: 블로그 크롤링

```bash
scrapy crawl site \
  -a seed="https://blog.example.com" \
  -a allowed_domains="blog.example.com" \
  -a max_pages=50
```

### 예시 2: React 앱 크롤링 (렌더링 필요)

```bash
scrapy crawl site \
  -a seed="https://react-app.com" \
  -a allowed_domains="react-app.com" \
  -a render=1 \
  -a max_pages=100
```

### 예시 3: 정적 사이트 (빠른 크롤링)

```bash
scrapy crawl site \
  -a seed="https://docs.example.com" \
  -a allowed_domains="docs.example.com" \
  -a render=0 \
  -a max_pages=200
```

### 예시 4: NVIDIA DRIVE OS 문서

```bash
scrapy crawl site \
  -a seed="https://developer.nvidia.com/docs/drive/drive-os/6.0.10/public/drive-os-linux-sdk/api_reference/index.html" \
  -a allowed_domains="developer.nvidia.com" \
  -a out_dir="./nvidia_docs" \
  -a max_pages=500 \
  -a max_depth=4 \
  -a render=0
```

## ⚡ 성능 최적화

### 빠른 크롤링 (정적 사이트)

```bash
scrapy crawl site \
  -a render=0 \              # Playwright 비활성화
  -a include_css_bg=0 \      # CSS 배경 비활성화
  -a max_pages=1000
```

### 느리지만 완전한 크롤링 (SPA)

```bash
scrapy crawl site \
  -a render=1 \              # Playwright 활성화
  -a include_css_bg=1 \      # CSS 배경 활성화
  -a max_pages=100
```

## 🔧 설정 수정

`site_crawler/settings.py` 파일에서:

```python
# 동시 요청 수
CONCURRENT_REQUESTS = 16

# 다운로드 지연
DOWNLOAD_DELAY = 0.25

# Playwright 페이지 수
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
```

## ❓ 문제 해결

### "scrapy: command not found"

```bash
pip install scrapy
```

### "playwright: command not found"

```bash
pip install playwright
playwright install chromium
```

### 크롤링이 너무 느림

- `render=0` 설정 (Playwright 비활성화)
- `include_css_bg=0` 설정
- `max_depth=2` (깊이 줄이기)
- `CONCURRENT_REQUESTS=32` (동시 요청 증가)

### 메모리 부족

- `max_pages` 줄이기
- `PLAYWRIGHT_MAX_PAGES_PER_CONTEXT=2` (브라우저 페이지 수 줄이기)

### 특정 사이트가 차단함

- `DOWNLOAD_DELAY=2` (지연 시간 증가)
- User-Agent 변경

## 📝 데이터 처리

### JSONL 읽기 (Python)

```python
import json

with open('output/pages.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        page = json.loads(line)
        print(f"Title: {page['title']}")
        print(f"Text: {page['text'][:100]}...")
        print()
```

### JSONL → CSV 변환

```python
import json
import csv

pages = []
with open('output/pages.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        pages.append(json.loads(line))

with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['url', 'title', 'text'])
    writer.writeheader()
    for page in pages:
        writer.writerow({
            'url': page['url'],
            'title': page['title'],
            'text': page['text']
        })
```

## 🆚 vs 내 Doxygen 크롤러

| 항목 | Scrapy 크롤러 | Doxygen 크롤러 |
|------|--------------|----------------|
| **설치** | 복잡 (4개 패키지) | 간단 (2개 패키지) |
| **실행** | 명령줄 | GUI ✅ |
| **속도** | 중간 | 빠름 ✅ |
| **렌더링** | Playwright ✅ | 없음 |
| **용도** | 모든 웹사이트 ✅ | Doxygen만 |
| **출력** | JSONL | TXT ✅ |
| **이미지** | 다운로드 ✅ | 없음 |

## 💡 언제 사용?

### Scrapy 크롤러 사용:
- ✅ React/Vue/Angular 등 SPA 사이트
- ✅ 다양한 웹사이트 크롤링
- ✅ 이미지 수집 필요
- ✅ 대량 크롤링 (1000+ 페이지)

### Doxygen 크롤러 사용:
- ✅ Doxygen API 문서
- ✅ 정적 HTML 문서
- ✅ GUI 선호
- ✅ TXT 파일 출력 필요

## 📄 라이센스

MIT License

## 🤝 크레딧

Original: https://github.com/yourusername/site-crawler-for-llm
