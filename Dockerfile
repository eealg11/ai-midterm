# STREAMING_CHUNK:Configuring Docker container setup for Cloud Run deployment...
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# Cloud Run 환경변수 지정 (PORT 8080)
ENV PORT 8080

# Gunicorn을 이용한 고성능 WSGI 서버 실행
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
