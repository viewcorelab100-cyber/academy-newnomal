# API 사용 예제

## 인증

### 1. 로그인
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@academy.com",
    "password": "admin123"
  }'
```

응답:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

이후 모든 요청에 헤더 추가:
```
Authorization: Bearer {access_token}
```

## 학생 관리

### 2. 학생 등록
```bash
curl -X POST "http://localhost:8000/students" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김철수",
    "phone": "010-1234-5678",
    "parent_phone": "010-9876-5432",
    "school": "서울고등학교",
    "grade": "고3",
    "notes": "수학 특별 관리 필요"
  }'
```

### 3. 학생 목록 조회
```bash
curl -X GET "http://localhost:8000/students?is_active=true" \
  -H "Authorization: Bearer {token}"
```

## 반 관리

### 4. 반 생성
```bash
curl -X POST "http://localhost:8000/classes" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "수학 심화반",
    "subject": "수학",
    "teacher": "박선생",
    "schedule": "월수금 19:00-21:00",
    "monthly_fee": 500000
  }'
```

## 수강 관리

### 5. 수강 등록
```bash
curl -X POST "http://localhost:8000/enrollments" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "class_id": 1,
    "start_date": "2024-01-01"
  }'
```

## 출석 체크

### 6. 등원 체크
```bash
curl -X POST "http://localhost:8000/attendance/check" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "type": "in"
  }'
```

### 7. 하원 체크
```bash
curl -X POST "http://localhost:8000/attendance/check" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "type": "out"
  }'
```

## 청구/결제

### 8. 월별 청구 생성
```bash
curl -X POST "http://localhost:8000/billing/run/2024-01" \
  -H "Authorization: Bearer {token}"
```

응답:
```json
{
  "month": "2024-01",
  "created_count": 15,
  "invoice_ids": [1, 2, 3, ...]
}
```

### 9. 청구서 목록 조회
```bash
curl -X GET "http://localhost:8000/billing/invoices?month=2024-01&status=UNPAID" \
  -H "Authorization: Bearer {token}"
```

### 10. 납부 처리
```bash
curl -X PATCH "http://localhost:8000/billing/invoices/1" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "PAID"
  }'
```

### 11. 미납자 알림 발송
```bash
curl -X POST "http://localhost:8000/billing/notify-overdue/2024-01" \
  -H "Authorization: Bearer {token}"
```

## 상담 노트

### 12. 상담 노트 작성 (비공개)
```bash
curl -X POST "http://localhost:8000/counseling/notes" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "content": "오늘 수학 성적이 많이 향상되었습니다. 계속 격려 필요.",
    "tags": "성적,긍정적",
    "visibility": "PRIVATE"
  }'
```

### 13. 상담 노트 작성 및 학부모 공유
```bash
curl -X POST "http://localhost:8000/counseling/notes" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "content": "이번 주 수학 모의고사 결과가 좋았습니다. 계속 노력하고 있습니다.",
    "tags": "시험,성적",
    "visibility": "SHARED"
  }'
```
※ `SHARED`로 설정하면 자동으로 학부모에게 카카오톡 알림이 발송됩니다.

### 14. 학생별 상담 내역 조회
```bash
curl -X GET "http://localhost:8000/counseling/notes/student/1" \
  -H "Authorization: Bearer {token}"
```

## 시퀀스 다이어그램 기반 워크플로우

### 워크플로우 1: 월 청구 프로세스
```bash
# 1. 매월 1일 청구서 자동 생성
curl -X POST "http://localhost:8000/billing/run/2024-01" -H "Authorization: Bearer {token}"

# 2. 납부 기한 후 미납자 알림
curl -X POST "http://localhost:8000/billing/notify-overdue/2024-01" -H "Authorization: Bearer {token}"

# 3. 학부모 납부 완료 후 상태 업데이트
curl -X PATCH "http://localhost:8000/billing/invoices/1" \
  -H "Authorization: Bearer {token}" \
  -d '{"status": "PAID"}'
```

### 워크플로우 2: 학생 상담 및 알림
```bash
# 1. 상담 메모 작성
curl -X POST "http://localhost:8000/counseling/notes" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "student_id": 1,
    "content": "이번 주 학습 태도가 매우 좋았습니다.",
    "visibility": "SHARED"
  }'
# → 자동으로 학부모에게 카카오톡 발송
```

### 워크플로우 3: 출석 체크
```bash
# 1. 학생 등원
curl -X POST "http://localhost:8000/attendance/check" \
  -H "Authorization: Bearer {token}" \
  -d '{"student_id": 1, "type": "in"}'
# → 자동으로 학부모에게 "등원 완료" 카카오톡 발송

# 2. 학생 하원
curl -X POST "http://localhost:8000/attendance/check" \
  -H "Authorization: Bearer {token}" \
  -d '{"student_id": 1, "type": "out"}'
# → 자동으로 학부모에게 "하원 완료" 카카오톡 발송
```

