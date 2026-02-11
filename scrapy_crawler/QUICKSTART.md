# 🚀 빠른 시작 가이드

## 1️⃣ 설치 (처음 1번만)

```bash
setup.bat 더블클릭
```

**또는 수동 설치:**
```bash
pip install scrapy scrapy-playwright readability-lxml
playwright install chromium
```

## 2️⃣ 실행

### 간단한 예시

```bash
run.bat
```

### 커스텀 URL

```bash
scrapy crawl site -a seed="https://example.com" -a allowed_domains="example.com" -a max_pages=100
```

### NVIDIA 문서

```bash
run_nvidia.bat
```

## 3️⃣ 결과 확인

```
./output/pages.jsonl
```

각 줄 = 1개 페이지 (JSON 형식)

## 💡 팁

**빠른 크롤링 (정적 사이트):**
```bash
scrapy crawl site -a seed="URL" -a allowed_domains="DOMAIN" -a render=0
```

**완전한 크롤링 (React/SPA):**
```bash
scrapy crawl site -a seed="URL" -a allowed_domains="DOMAIN" -a render=1
```

**적은 페이지:**
```bash
scrapy crawl site -a seed="URL" -a allowed_domains="DOMAIN" -a max_pages=10
```

## ❓ 도움말

자세한 내용은 `README.md`를 참고하세요.
