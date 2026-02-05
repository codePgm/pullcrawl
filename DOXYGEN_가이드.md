# Doxygen 문서 크롤러

### NVIDIA DRIVE OS 문서는 Doxygen으로 생성된 API 문서

일반 크롤러로는 **1개의 페이지만** 크롤링되는 이유:
- Doxygen 문서는 특별한 구조를 가지고 있습니다
- 주요 페이지들이 `modules.html`, `classes.html`, `files.html` 등으로 분리되어 있습니다
- 일반 링크 추출 방식으로는 찾을 수 없습니다

### 해결 방법: Doxygen 전용 크롤러 사용!

이 크롤러는:
- Doxygen의 공통 페이지 자동 탐색 (modules.html, classes.html 등)
- 모든 HTML 파일 자동 수집
- **100개 이상의 API 문서 페이지 크롤링 가능!**

---

## 빠른 시작

### 가장 쉬운 방법 (GUI)

```
run_doxygen_gui.bat 을 더블클릭!
```

### 명령줄 방법

```batch
run_doxygen.bat "https://developer.nvidia.com/docs/drive/drive-os/6.0.10/public/drive-os-linux-sdk/api_reference/index.html"
```

---

## 상세 사용법

### GUI 버전

#### 1. 실행
```batch
run_doxygen_gui.bat
```

#### 2. 설정
- **문서 URL**: Doxygen 문서의 index.html URL 입력
- **최대 페이지 수**: 500 (Doxygen 문서는 보통 100~300 페이지)
- **요청 간격**: 1.0초 (빠른 크롤링)
- **크롤링 전략**:
  - **적극적**: 모든 .html 파일 수집 (추천!)
  - **보통**: API 관련 페이지만
  - **보수적**: 주요 페이지만

#### 3. 결과
```
doxygen_crawl/
├── crawl_원문/전체_크롤링_결과.txt
├── crawl_요약본/크롤링_요약.txt
└── crawlJson/crawl_results.json
```

---

### 명령줄 버전

#### 기본 사용
```batch
run_doxygen.bat "https://developer.nvidia.com/docs/.../index.html"
```

#### 옵션 지정
```batch
run_doxygen.bat "URL" [최대페이지] [간격] [출력폴더]

예:
run_doxygen.bat "URL" 300 1.0 nvidia_api
```

#### Python 직접 실행
```batch
python doxygen_crawler.py "URL" --max-pages 300 --delay 1.0
```

---

## Doxygen 크롤러의 작동 방식

### 1단계: 시드 페이지 탐색
자동으로 다음 페이지를 확인합니다:
- `index.html` - 메인 페이지
- `modules.html` - 모듈 목록
- `namespaces.html` - 네임스페이스
- `classes.html` - 클래스 목록
- `files.html` - 파일 목록
- `annotated.html` - 주석 목록
- `functions.html` - 함수 목록
- `globals.html` - 전역 변수/함수
- `pages.html` - 추가 페이지

### 2단계: 링크 수집
각 시드 페이지에서 **모든 HTML 링크**를 수집합니다.

예상 결과:
```
✓ 발견된 HTML 페이지: 150개

발견된 페이지 예시:
  1. annotated.html
  2. class_nv_media_i_c_p.html
  3. class_nv_media_i_d_p.html
  4. group__nvmedia__api.html
  5. struct_nv_media_device.html
  ... 외 145개
```

### 3단계: 각 페이지 크롤링
발견된 모든 페이지를 순차적으로 크롤링합니다.

---

## 예상 결과 (NVIDIA DRIVE OS)

### 일반 크롤러
```
발견된 링크: 1개
총 페이지: 1
```

### Doxygen 크롤러
```
발견된 HTML 페이지: 150개
총 페이지: 150
성공: 148
실패: 2
```

---

## 실전 예제

### NVIDIA DRIVE OS API 크롤링

```batch
run_doxygen_gui.bat
```

설정:
- URL: `https://developer.nvidia.com/docs/drive/drive-os/6.0.10/public/drive-os-linux-sdk/api_reference/index.html`
- 최대 페이지: 300
- 요청 간격: 1.0초
- 전략: 적극적

예상 소요 시간: 약 5-10분
예상 페이지 수: 100-200개

### 결과 확인

```
doxygen_crawl/
├── crawl_원문/
│   ├── 001_NVIDIA_DRIVE_OS_API_Reference_20240205_143022.txt
│   ├── 002_Module_List_20240205_143022.txt
│   ├── 003_[PDF]_User_Manual_20240205_143022.txt         ← PDF를 TXT로 변환!
│   ├── 004_NvMedia_API_20240205_143022.txt
│   ├── 005_Thermal_Monitor_20240205_143022.txt
│   └── ... (각 페이지마다 개별 파일!)
├── crawl_요약본/
│   └── 크롤링_요약.txt (전체 파일 목록)
└── crawlJson/
    └── crawl_results.json (JSON 데이터)
```

**400개 페이지 크롤링 시 → 400개의 개별 TXT 파일 생성!**
**PDF 파일도 자동으로 TXT로 변환!**

### 파일명 규칙

각 파일은 다음 형식으로 저장됩니다:
```
{순번:3자리}_{페이지제목}_{크롤링시간}.txt
{순번:3자리}_[PDF]_{페이지제목}_{크롤링시간}.txt  ← PDF 파일인 경우

예시:
001_NVIDIA_DRIVE_OS_Linux_SDK_API_Reference_20240205_143022.txt
002_Modules_20240205_143022.txt
003_[PDF]_Installation_Guide_20240205_143022.txt         ← PDF!
004_NvMedia_ICP_Class_Reference_20240205_143022.txt
150_Thermal_Monitor_API_20240205_143022.txt
```

**장점:**
- 각 API 문서를 개별 관리
- 필요한 파일만 열람
- 파일명으로 내용 파악
- 크롤링 시간 기록
- PDF도 자동으로 TXT 변환!

---

## 🔧 고급 설정

### 대량 API 문서 크롤링
```batch
python doxygen_crawler.py "URL" --max-pages 1000 --delay 0.5
```

### 빠른 테스트
```batch
python doxygen_crawler.py "URL" --max-pages 50 --delay 0.5
```

### 커스텀 출력 폴더
```batch
python doxygen_crawler.py "URL" --output-dir "my_api_docs"
```

---

## FAQ

**Q: 왜 일반 크롤러로는 1개만 크롤링되나요?**
A: Doxygen 문서는 특별한 구조를 가지고 있어서 일반적인 사이드바/네비게이션 링크 추출로는 찾을 수 없습니다. Doxygen 전용 크롤러가 필요합니다.

**Q: Doxygen 크롤러와 일반 크롤러의 차이는?**
A: 
- 일반 크롤러: 사이드바/네비게이션 링크만 추출
- Doxygen 크롤러: modules.html, classes.html 등 Doxygen 특화 페이지 자동 탐색

**Q: 얼마나 많은 페이지를 크롤링할 수 있나요?**
A: Doxygen 문서의 크기에 따라 다릅니다. NVIDIA DRIVE OS의 경우 약 100-200개의 API 페이지가 있습니다.

**Q: 크롤링 속도를 높이려면?**
A: `--delay` 값을 낮추세요 (예: 0.5초). 단, 서버에 부담을 주지 않도록 주의하세요.

**Q: 이 크롤러는 Doxygen 문서만 가능한가요?**
A: 네, Doxygen으로 생성된 API 문서 전용입니다. 일반 웹사이트는 기존 크롤러(V2)를 사용하세요.

**Q: 어떤 크롤러를 사용해야 하나요?**
A:
- NVIDIA DRIVE OS 같은 Doxygen 문서 → `run_doxygen_gui.bat`
- 일반 문서 사이트 → `run_gui_v2.bat`

---

## 제공 파일

### Doxygen 크롤러 (NVIDIA용)
- `doxygen_crawler_gui.py` - GUI 프로그램
- `doxygen_crawler.py` - 명령줄 프로그램
- `run_doxygen_gui.bat` - GUI 실행
- `run_doxygen.bat` - 명령줄 실행

### 일반 크롤러 (다른 사이트용)
- `doc_crawler_gui_v2.py`
- `doc_crawler_v2.py`
- `run_gui_v2.bat`
- `run_crawler_v2.bat`

---

## 결론

NVIDIA DRIVE OS 같은 Doxygen 문서는:
1. **Doxygen 크롤러 사용**
2. 100개 이상의 페이지 크롤링 가능
3. modules.html, classes.html 등 자동 탐색
4. 완전한 API 문서 수집

---

## 지금 바로 시작하기

```
1. run_doxygen_gui.bat 더블클릭
2. NVIDIA URL 입력
3. "크롤링 시작" 클릭
4. 결과 확인!
```
