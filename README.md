# 🕷️ Doxygen 문서 크롤러

Doxygen으로 생성된 API 문서를 자동으로 크롤링하여 TXT 파일로 저장하는 도구입니다.

## 📁 프로젝트 구조

```
doxygen_crawler_refactored/
├── 📁 config/                  # 설정
│   ├── __init__.py
│   └── constants.py           # 상수 정의
│
├── 📁 utils/                   # 유틸리티 모듈
│   ├── __init__.py
│   ├── url_utils.py           # URL 처리
│   ├── text_utils.py          # 텍스트 추출
│   ├── pdf_utils.py           # PDF 처리
│   └── file_utils.py          # 파일 작업
│
├── crawler.py                 # 메인 크롤러 로직
├── gui.py                     # GUI 애플리케이션
├── run.bat                    # 실행 파일 (Windows)
└── README.md                  # 이 파일
```

## 🚀 사용 방법

### 1. 간단 실행 (GUI)

```bash
# Windows
run.bat 더블클릭

# Python 직접 실행
python gui.py
```

### 2. 설정

- **URL**: 크롤링할 Doxygen 문서의 시작 URL
- **최대 페이지**: 수집할 최대 페이지 수 (기본: 500)
- **요청 간격**: 페이지 간 대기 시간 (초) (기본: 1.0)
- **출력 폴더**: 결과 저장 위치 (기본: doxygen_crawl)

### 3. 결과

```
doxygen_crawl/
├── crawl_원문/                    # 크롤링한 원본 파일들
│   ├── 001_index_20240210.txt
│   ├── 002_modules_20240210.txt
│   └── ...
│
└── crawlJson/                     # JSON 데이터
    └── crawl_results.json
```

## ✨ 주요 기능

- ✅ **Doxygen 전용 최적화** - 자동으로 주요 페이지 탐색
- ✅ **PDF 지원** - PDF 파일도 텍스트로 변환
- ✅ **중복 제거** - 같은 페이지 중복 크롤링 방지
- ✅ **깨끗한 출력** - 개별 TXT 파일로 저장
- ✅ **진행 상황 표시** - 실시간 로그 확인
- ✅ **중단 가능** - 언제든지 중지 가능

## 📋 요구 사항

- Python 3.8 이상
- 필수 패키지:
  - `requests` - HTTP 요청
  - `beautifulsoup4` - HTML 파싱
  - `pypdf` - PDF 처리 (선택)

## 🔧 모듈 설명

### `config/constants.py`
프로그램 전체에서 사용하는 상수 정의

### `utils/url_utils.py`
URL 정규화, 검증, 파싱 등 URL 관련 유틸리티

### `utils/text_utils.py`
HTML에서 제목, 본문, 코드 블록 추출

### `utils/pdf_utils.py`
PDF 파일에서 텍스트 추출

### `utils/file_utils.py`
파일명 정리, 타임스탬프 생성, 디렉토리 생성

### `crawler.py`
메인 크롤러 로직 - 페이지 탐색, 데이터 수집, 저장

### `gui.py`
사용자 인터페이스 - Tkinter 기반 GUI

## 💡 사용 예시

### NVIDIA DRIVE OS 문서 크롤링

```
URL: https://developer.nvidia.com/docs/drive/drive-os/6.0.10/public/drive-os-linux-sdk/api_reference/index.html
최대 페이지: 500
요청 간격: 1.0
```

결과: 430개 페이지의 API 문서가 개별 TXT 파일로 저장됩니다.

## 🐛 문제 해결

### "모듈을 찾을 수 없습니다"
```bash
pip install requests beautifulsoup4 pypdf
```

### "PDF 라이브러리 없음"
PDF 기능은 선택사항입니다. HTML만 크롤링하려면 무시해도 됩니다.
```bash
pip install pypdf
```

## 📝 라이센스

MIT License

## 🤝 기여

버그 리포트나 기능 제안은 환영합니다!
