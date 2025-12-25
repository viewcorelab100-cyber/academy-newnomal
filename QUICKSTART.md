# 빠른 시작 가이드

## 1분 안에 실행하기

### 1단계: 가상환경 및 의존성 설치
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2단계: 환경 변수 설정
`.env` 파일 생성 (프로젝트 루트):
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/academy_db
SECRET_KEY=change-this-to-a-long-random-string-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
KAKAO_REST_API_KEY=your-key
KAKAO_SENDER_KEY=your-key
KAKAO_ALIMTALK_TEMPLATE_IN=template-code
KAKAO_ALIMTALK_TEMPLATE_OUT=template-code
KAKAO_ALIMTALK_TEMPLATE_COUNSELING=template-code
KAKAO_ALIMTALK_TEMPLATE_BILLING=template-code
KAKAO_ALIMTALK_TEMPLATE_OVERDUE=template-code
```

### 3단계: PostgreSQL 설정
```sql
-- psql 또는 pgAdmin에서 실행
CREATE DATABASE academy_db;
```

### 4단계: 데이터베이스 초기화
```bash
python scripts/init_db.py
```

출력:
```
데이터베이스 테이블 생성 중...
✓ 테이블 생성 완료
✓ 초기 관리자 계정 생성 완료
  이메일: admin@academy.com
  비밀번호: admin123
```

### 5단계: 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6단계: 접속
- **메인 페이지**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **초기 계정**: admin@academy.com / admin123

## 주요 API 테스트

### 1. 로그인
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@academy.com", "password": "admin123"}'
```

### 2. 학생 등록
```bash
curl -X POST "http://localhost:8000/students" \
  -H "Authorization: Bearer {위에서_받은_토큰}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김철수",
    "parent_phone": "010-1234-5678",
    "school": "서울고",
    "grade": "고3"
  }'
```

### 3. 출석 체크
```bash
curl -X POST "http://localhost:8000/attendance/check" \
  -H "Authorization: Bearer {토큰}" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "type": "in"}'
```

## 시퀀스 다이어그램 구현 확인

제공하신 3개의 시퀀스 다이어그램이 모두 구현되었습니다:

### ✅ 청구/결제 프로세스
- `/billing/run/{month}` - 월별 자동 청구 생성
- `/billing/notify-overdue/{month}` - 미납 알림
- `/billing/invoices/{id}` - 납부 상태 업데이트

### ✅ 상담 노트 작성 및 메시지 발송
- `/counseling/notes` - 상담 메모 저장
- visibility=SHARED 시 자동 카카오톡 발송

### ✅ 출석 체크
- `/attendance/check` - 등원/하원 기록
- 자동 학부모 알림 (등원/하원 템플릿)

## 다음 단계

1. **보안**: `.env`의 `SECRET_KEY`를 변경하세요
2. **카카오톡 API**: 실제 카카오톡 API 키로 교체하세요
3. **커스터마이징**: 학원별 요구사항에 맞게 API를 확장하세요
4. **프론트엔드**: HTML 템플릿을 개선하거나 React/Vue.js로 교체하세요

## 문제 해결

### PostgreSQL 연결 오류
- PostgreSQL이 실행 중인지 확인
- `.env`의 `DATABASE_URL` 확인

### 포트 충돌
- 다른 포트로 실행: `uvicorn app.main:app --port 8080`

### 카카오톡 발송 실패
- MVP에서는 로그만 기록됩니다
- 실제 발송을 위해 `app/services/kakao.py`의 주석을 해제하세요

## 추가 문서

- `README.md` - 프로젝트 전체 개요
- `docs/system-overview.md` - 시스템 아키텍처
- `docs/api-examples.md` - API 사용 예제
- `docs/deployment.md` - 프로덕션 배포 가이드

