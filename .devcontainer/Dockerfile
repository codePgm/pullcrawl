# Python 3.12 기반 (안정적이고 Scrapy/Playwright 호환)
FROM python:3.12-slim

# 메타데이터
LABEL maintainer="crawler-dev"
LABEL description="Web Crawler Development Environment"

# 비-root 사용자 생성
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # 기본 도구
    git \
    curl \
    wget \
    vim \
    nano \
    tree \
    # 빌드 도구
    build-essential \
    # Playwright 의존성
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    # PDF 처리
    poppler-utils \
    # 정리
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# 비-root 사용자 생성
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Python 패키지 업그레이드
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 기본 Python 패키지 설치 (개발 도구)
RUN pip install --no-cache-dir \
    # 코드 품질
    black \
    flake8 \
    pylint \
    mypy \
    ruff \
    # 테스팅
    pytest \
    pytest-cov \
    pytest-asyncio \
    # 디버깅
    ipython \
    ipdb \
    # 유틸리티
    python-dotenv

# 작업 디렉토리
WORKDIR /workspace

# 사용자 전환
USER $USERNAME

# Playwright 브라우저 설치 (vscode 사용자로)
ENV PLAYWRIGHT_BROWSERS_PATH=/home/$USERNAME/.cache/ms-playwright
RUN pip install --no-cache-dir playwright==1.40.0 \
    && playwright install chromium

# 기본 쉘 설정
SHELL ["/bin/bash", "-c"]

# 환경 변수
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 헬스체크 (선택사항)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python --version || exit 1

# 기본 명령어
CMD ["/bin/bash"]
