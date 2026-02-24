# 🕷️ 통합 웹 크롤러

하나의 GUI에서 두 가지 크롤러를 선택하여 사용할 수 있습니다!

## ✨ 두 가지 크롤러

### 🚀 간단 크롤러 (Simple Crawler)

**용도:**
- Doxygen 문서 (NVIDIA, OpenCV 등)
- Sphinx 문서 (Python Docs, ROS 등)
- 정적 HTML 웹사이트

**특징:**
- ✅ 빠름 (1분 내외)
- ✅ 간단 (설치 쉬움)
- ✅ GUI 내에서 직접 실행
- ✅ TXT 파일 출력

**요구사항:**
```bash
pip install requests beautifulsoup4 pypdf
```

### ⚡ 고급 크롤러 (Advanced Crawler)

**용도:**
- React/Vue/Angular 사이트
- SPA (Single Page Application)
- JavaScript로 생성되는 콘텐츠

**특징:**
- ✅ SPA 지원 (Playwright 렌더링)
- ✅ 고급 기능 (이미지 다운로드, CSS 배경 추출)
- ⚠️ 느림 (30분~1시간)
- ⚠️ 복잡 (설치 많음)
- ✅ JSONL 출력

**요구사항:**
```bash
pip install scrapy scrapy-playwright readability-lxml
playwright install chromium
```

---

## 🚀 빠른 시작

### 1단계: 설치

```bash
# 기본 설치 (간단 크롤러만)
run.bat 더블클릭
```

**고급 크롤러도 사용하려면:**
```bash
setup_advanced.bat 더블클릭
```

### 2단계: 실행

```bash
run.bat 더블클릭
```

### 3단계: GUI에서 선택

```
┌─────────────────────────────────────┐
│ 크롤러 선택:                        │
│ ● 간단 크롤러 (추천)                │
│ ○ 고급 크롤러                       │
└─────────────────────────────────────┘
```

---

## 📁 프로젝트 구조

```
unified_crawler/
├── launcher.py              # 통합 GUI 런처
├── run.bat                  # 실행 파일
├── setup_advanced.bat       # 고급 크롤러 설치
│
├── simple_crawler/          # 간단 크롤러
│   ├── config/
│   ├── utils/
│   └── crawler.py
│
└── scrapy_crawler/          # 고급 크롤러 (Scrapy)
    ├── site_crawler/
    │   ├── spiders/
    │   └── ...
    └── scrapy.cfg
```

---

## 💡 어떤 크롤러를 선택할까?

### 간단 크롤러 선택:

✅ **Doxygen 문서**
- NVIDIA DRIVE OS
- OpenCV Documentation
- ROS Documentation

✅ **Sphinx 문서**
- Python Documentation
- Django Documentation

✅ **정적 HTML**
- 일반 블로그
- 위키 사이트

### 고급 크롤러 선택:

✅ **SPA 사이트**
- Vert.x Documentation
- React Documentation
- Vue.js Documentation

✅ **JavaScript 많은 사이트**
- 내용이 동적으로 로드되는 사이트
- 스크롤해야 내용이 나타나는 사이트

---

## 🎯 사용 예시

### 예시 1: NVIDIA 문서 (간단 크롤러)

```
크롤러: 🚀 간단 크롤러
URL: https://developer.nvidia.com/docs/drive/drive-os/.../index.html
최대 페이지: 500
출력 폴더: ./nvidia_docs

→ 결과: TXT 파일 430개
→ 시간: 약 5분
```

### 예시 2: Vert.x 문서 (고급 크롤러)

```
크롤러: ⚡ 고급 크롤러
URL: https://vertx.io/docs/vertx-core/java/
최대 페이지: 100
깊이: 4
렌더링: ☑ 사용

→ 결과: JSONL 파일
→ 시간: 약 30분
```

---

## 📊 비교표

| 항목 | 간단 크롤러 | 고급 크롤러 |
|------|-----------|-----------|
| **속도** | ⚡⚡⚡ 빠름 (5분) | 🐢 느림 (30분+) |
| **설치** | ✅ 간단 (2개 패키지) | ⚠️ 복잡 (4개 패키지 + 브라우저) |
| **SPA 지원** | ❌ 없음 | ✅ 있음 (Playwright) |
| **출력** | TXT | JSONL |
| **GUI 실행** | ✅ GUI 내에서 | ⚠️ 별도 창 |
| **이미지 수집** | ❌ | ✅ |
| **적합한 사이트** | Doxygen, Sphinx | React, Vue, SPA |

---

## ⚙️ 설정

### 공통 설정

- **최대 페이지**: 크롤링할 최대 페이지 수
- **출력 폴더**: 결과 저장 위치

### 간단 크롤러 설정

- **요청 간격**: 페이지 간 대기 시간 (초)

### 고급 크롤러 설정

- **깊이 제한**: 링크를 따라갈 최대 깊이
- **Playwright 렌더링**: JavaScript 실행 여부

---

## 🐛 문제 해결

### "간단 크롤러를 찾을 수 없습니다"

```bash
# simple_crawler 폴더가 있는지 확인
# 없으면 doxygen_crawler_refactored 내용을 복사
```

### "Scrapy를 찾을 수 없습니다"

```bash
# 고급 크롤러 설치 필요
setup_advanced.bat
```

### "모듈을 찾을 수 없습니다"

```bash
# 패키지 재설치
pip install requests beautifulsoup4 pypdf
```

### 고급 크롤러가 멈춤

- 정상입니다! Playwright가 브라우저를 실행 중
- 별도 창에서 로그 확인
- 30분~1시간 소요 가능

---

## 📝 출력 형식

### 간단 크롤러

```
./crawl_output/
├── crawl_원문/
│   ├── 001_index_20240210.txt
│   ├── 002_modules_20240210.txt
│   └── ...
└── crawlJson/
    └── crawl_results.json
```

### 고급 크롤러

```
./crawl_output/
└── pages.jsonl    # 각 줄이 1개 페이지 (JSON)
```

---

## 💡 팁

### 1. 먼저 간단 크롤러로 시도

대부분의 문서 사이트는 간단 크롤러로 충분합니다.

### 2. 고급 크롤러는 필요할 때만

SPA가 확실할 때만 고급 크롤러 사용하세요.

### 3. 소량으로 먼저 테스트

```
최대 페이지: 10
→ 테스트 후 늘리기
```

### 4. 출력 폴더 분리

```
NVIDIA: ./nvidia_docs
Vert.x: ./vertx_docs
```

---

## 🆚 언제 어떤 크롤러?

```
사이트 확인 → HTML 소스 보기 (Ctrl+U)

├─ <div> <p> <a> 태그 많이 보임
│  → 간단 크롤러 ✅
│
└─ <div id="app"></div> <script> 만 보임
   → 고급 크롤러 ⚡
```

---

## 📄 라이센스

MIT License

## 🙏 크레딧

- Simple Crawler: 정적 HTML 전용 고속 크롤러
- Advanced Crawler: Scrapy + Playwright 기반 SPA 크롤러

---

도커 사용법
devcontainer.json :
    vscode 에서 도커를 실행하여 도커 환경에서 vscode 를 실행하게 만들기 위해서 사용함 
    여러 컴퓨터에서 개발 할 시 개발 환경이 달라서 안될 수 도 있는데 이걸 해결 하기위해서 도커 에서 vscode 를 실행 시킴

    **설치:**
    1. VS Code 설치
    2. "Dev Containers" 확장 설치
    3. Docker Desktop 실행

    **사용:**
    1. VS Code에서 pullcrawl 폴더 열기
    2. Ctrl+Shift+P (명령 팔레트)
    3. "Dev Containers: Reopen in Container" 선택
    4. 자동으로 컨테이너 생성 및 접속
    5. VS Code 안에서 코드 편집/실행

Dockerfile :
    도커 이미지를 생성

    # Docker Desktop에서
    cd pullcrawl

    # 이미지 빌드
    docker build -t crawler -f .devcontainer/Dockerfile .

    # 컨테이너 실행
    docker run -it -v ${PWD}/crawl_output:/app/crawl_output crawler

    # 크롤러 실행
    python3 launcher_CLI.py -t simple -u "https://example.com" -m 10
                                                "URL"              최대페이지