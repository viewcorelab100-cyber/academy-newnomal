# 배포 가이드

## 로컬 개발 환경 설정

### 1. 필수 요구사항
- Python 3.9+
- PostgreSQL 12+
- Git

### 2. 프로젝트 클론 및 설정
```bash
# 가상환경 생성
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. PostgreSQL 데이터베이스 생성
```sql
CREATE DATABASE academy_db;
CREATE USER academy_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE academy_db TO academy_user;
```

### 4. 환경 변수 설정
`.env` 파일을 열어 다음 값들을 실제 환경에 맞게 수정:
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `SECRET_KEY`: JWT 서명용 비밀 키 (긴 랜덤 문자열)
- 카카오톡 API 키 및 템플릿 코드

### 5. 데이터베이스 초기화
```bash
python scripts/init_db.py
```

### 6. 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면:
- 메인 페이지: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 프로덕션 배포

### 방법 1: Docker (권장)

`Dockerfile` 생성:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`docker-compose.yml` 생성:
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: academy_db
      POSTGRES_USER: academy_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - .env

volumes:
  postgres_data:
```

실행:
```bash
docker-compose up -d
```

### 방법 2: 클라우드 플랫폼 (AWS, GCP, Azure)

#### AWS EC2 배포
1. EC2 인스턴스 생성 (Ubuntu 20.04)
2. 보안 그룹에서 포트 8000, 22 열기
3. SSH 접속 후 프로젝트 설정
4. Nginx 리버스 프록시 설정
5. Gunicorn으로 FastAPI 실행

#### Nginx 설정 예제
```nginx
server {
    listen 80;
    server_name academy.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Systemd 서비스 설정
`/etc/systemd/system/academy.service`:
```ini
[Unit]
Description=Academy Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/academy
Environment="PATH=/var/www/academy/venv/bin"
ExecStart=/var/www/academy/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

실행:
```bash
sudo systemctl enable academy
sudo systemctl start academy
```

### 방법 3: Vercel / Railway (간단한 배포)

**Railway 배포**:
1. Railway 계정 생성
2. GitHub 리포지토리 연결
3. PostgreSQL 플러그인 추가
4. 환경 변수 설정
5. 자동 배포

## 보안 체크리스트

프로덕션 배포 전 확인사항:

- [ ] `.env` 파일의 `SECRET_KEY`를 강력한 랜덤 문자열로 변경
- [ ] 초기 관리자 비밀번호 변경 (admin123 → 강력한 비밀번호)
- [ ] PostgreSQL 비밀번호 변경
- [ ] CORS 설정을 실제 도메인으로 제한
- [ ] HTTPS 적용 (Let's Encrypt)
- [ ] 데이터베이스 백업 설정
- [ ] 로그 모니터링 설정
- [ ] 카카오톡 API 키 보안 확인

## 모니터링 및 유지보수

### 로그 확인
```bash
# systemd 서비스 로그
sudo journalctl -u academy -f

# Docker 로그
docker-compose logs -f web
```

### 데이터베이스 백업
```bash
# PostgreSQL 백업
pg_dump -U academy_user academy_db > backup_$(date +%Y%m%d).sql

# 복원
psql -U academy_user academy_db < backup_20240101.sql
```

### 성능 모니터링
- CPU/메모리 사용량 체크
- API 응답 시간 모니터링
- 데이터베이스 쿼리 최적화
- 카카오톡 발송 성공률 추적

