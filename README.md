# 학원 관리 시스템 MVP

소규모 입시학원을 위한 경량 관리 시스템

## 핵심 기능
- 학생/반/수강 관리 (CRUD)
- **카카오 OAuth 학생 가입** - 초대 링크를 통한 간편 가입 ✨
- **QR 코드 출석 체크** - 학생별 고유 QR로 등원/하원 자동 기록
- 출석 체크 (등원/하원)
- 월별 자동 청구 및 결제 관리
- 상담 노트 작성
- 카카오톡 알림 (알림톡/친구톡)

## 기술 스택
- Backend: Python + FastAPI
- Frontend: Plain HTML + Vanilla JavaScript
- Database: SQLite (개발) / PostgreSQL (프로덕션)
- Auth: 
  - 관리자: JWT (이메일 기반)
  - 학생: Kakao OAuth 2.0
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
루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가:
```env
# Database
DATABASE_URL=sqlite:///./academy.db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Kakao OAuth (필수)
KAKAO_REST_KEY=your_kakao_rest_api_key
KAKAO_REDIRECT_URI=http://localhost:8000/auth/kakao/callback

# App
BASE_URL=http://localhost:8000
```

**카카오 개발자 콘솔 설정:**
1. https://developers.kakao.com/console 접속
2. 앱 생성 및 REST API 키 발급
3. "플랫폼" → Web 플랫폼 추가 → `http://localhost:8000`
4. "카카오 로그인" → Redirect URI 등록 → `http://localhost:8000/auth/kakao/callback`

자세한 설정 방법은 [docs/kakao-oauth-setup.md](docs/kakao-oauth-setup.md) 참고

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
- POST /students/{id}/invite - 초대 링크 생성
- GET /students/{id}/invite-status - 초대 상태 조회

### 학생 인증 (카카오 OAuth)
- GET /student/signup?token={token} - 초대 링크 진입
- GET /auth/kakao/start?state={state} - 카카오 로그인 시작
- GET /auth/kakao/callback - 카카오 콜백
- GET /student/signup/success - 가입 완료
- GET /student/qr/{qr_code} - 학생 QR 코드
- POST /student/checkin - QR 출석 체크

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

## 주요 기능 가이드

### 📱 학생 초대 및 카카오 연동
1. **관리자가 초대 링크 생성**
   - 학생 목록에서 "초대 링크 생성" 클릭
   - 24시간 유효한 고유 링크 생성
   
2. **학생이 카카오 로그인으로 가입**
   - 초대 링크 클릭 → 카카오 로그인
   - 자동으로 학생 계정과 카카오 연동
   
3. **QR 코드로 출석 체크**
   - 가입 완료 후 고유 QR 코드 발급
   - QR 스캔으로 등원/하원 자동 기록
   - 학부모에게 카카오톡 알림 자동 발송

자세한 내용: [docs/kakao-oauth-setup.md](docs/kakao-oauth-setup.md)

### 🎯 빠른 시작 가이드
- [QUICKSTART.md](QUICKSTART.md) - 전체 시스템 시작 가이드
- [QUICKSTART-QR.md](QUICKSTART-QR.md) - QR 출석 체크 가이드

## 📚 문서
- [system-overview.md](docs/system-overview.md) - 시스템 개요
- [authentication.md](docs/authentication.md) - 인증 시스템
- [kakao-oauth-setup.md](docs/kakao-oauth-setup.md) - 카카오 OAuth 설정 ✨
- [kakao-oauth-example.md](docs/kakao-oauth-example.md) - OAuth 플로우 예제 ✨
- [qr-attendance.md](docs/qr-attendance.md) - QR 출석 체크
- [student-management.md](docs/student-management.md) - 학생 관리
- [attendance.md](docs/attendance.md) - 출석 관리
- [deployment.md](docs/deployment.md) - 배포 가이드

