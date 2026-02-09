FROM python:3.12.12-bookworm

# 사용자 및 그룹 ID 설정
ARG UID
ARG GID

# 비대화형 모드 설정
ENV DEBIAN_FRONTEND=noninteractive

### SSH 서버 설정 ###

# 사용자 및 그룹 생성
RUN groupadd -g ${GID} developer \
    && useradd -m -u ${UID} -g ${GID} -s /bin/bash developer

# 필수 패키지 설치
RUN apt -y update && apt -y install --no-install-recommends \
    openssh-server && mkdir /var/run/sshd

# # SSH 키 생성
# RUN ssh-keygen -A

# SSH 디렉토리 생성 및 권한 설정
RUN mkdir -p /home/developer/.ssh
COPY id_ed25519.pub /home/developer/.ssh/authorized_keys
RUN chown -R developer:developer /home/developer/.ssh && \
    chmod 700 /home/developer/.ssh && \
    chmod 600 /home/developer/.ssh/authorized_keys

# SSH 설정: 비밀번호 인증 비활성화
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

# 포트 22 노출
EXPOSE 22

# SSH 데몬 실행
CMD ["/usr/sbin/sshd", "-D"]

### Python 환경 설정 ###
# OS 패키지: venv + 빌드/런타임 의존성 + Playwright 런타임 의존성
RUN apt update && apt install -y --no-install-recommends \
    python3-venv \
    build-essential \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg62-turbo-dev \
    libpq-dev \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*

# path 추가
ENV PATH="/home/developer/.local/bin:${PATH}"
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN printf '%s\n' \
  'export PLAYWRIGHT_BROWSERS_PATH=/ms-playwright' \
  > /etc/profile.d/playwright.sh \
  && chmod 644 /etc/profile.d/playwright.sh

# Playwright 브라우저 공용 경로 고정
RUN mkdir -p /ms-playwright && chmod 777 /ms-playwright

# 파이썬 패키지 설치(venv 쓰면 더 깔끔)
RUN pip install -U pip setuptools wheel
RUN pip install -U scrapy scrapy-playwright playwright readability-lxml w3lib lxml pillow

# system deps까지 같이 설치하려면 root에서 실행 필요
RUN playwright install --with-deps

# USER developer
WORKDIR /app
