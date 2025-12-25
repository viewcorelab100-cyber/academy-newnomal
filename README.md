# 학원 관리 시스템 MVP

소규모 입시학원을 위한 경량 관리 시스템

## 핵심 기능
- 학생/반/수강 관리 (CRUD)
- 출석 체크 (등원/하원)
- 월별 자동 청구 및 결제 관리
- 상담 노트 작성
- 카카오톡 알림 (알림톡/친구톡)

## 기술 스택
- Backend: Python + FastAPI
- Frontend: Plain HTML + Vanilla JavaScript
- Database: PostgreSQL
- Auth: JWT (이메일 기반)
- Messaging: KakaoTalk API

## 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 실제 값으로 수정
```

### 4. 데이터베이스 초기화
```bash
python scripts/init_db.py
```

### 5. 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버: http://localhost:8000
API 문서: http://localhost:8000/docs

## 프로젝트 구조
```
app/
├── main.py                 # FastAPI 앱 진입점
├── config.py              # 설정 (환경변수)
├── database.py            # DB 연결
├── models/                # SQLAlchemy 모델
├── schemas/               # Pydantic 스키마
├── api/                   # API 라우트
├── services/              # 비즈니스 로직
└── templates/             # HTML 템플릿

scripts/
└── init_db.py             # DB 초기화 스크립트

static/
├── css/
└── js/
```

## API 엔드포인트

### 인증
- POST /auth/login
- POST /auth/register (관리자 전용)

### 학생
- GET /students
- POST /students
- GET /students/{id}
- PATCH /students/{id}
- DELETE /students/{id}

### 반
- GET /classes
- POST /classes
- GET /classes/{id}
- PATCH /classes/{id}
- DELETE /classes/{id}

### 수강
- GET /enrollments
- POST /enrollments
- DELETE /enrollments/{id}

### 출석
- POST /attendance/check
- GET /attendance/student/{student_id}

### 청구/결제
- POST /billing/run/{month}
- GET /billing/invoices
- PATCH /billing/invoices/{id}
- POST /billing/notify-overdue/{month}/{cohort}

### 상담 노트
- POST /counseling/notes
- GET /counseling/notes/student/{student_id}

### 메시지
- POST /messages/kakao

