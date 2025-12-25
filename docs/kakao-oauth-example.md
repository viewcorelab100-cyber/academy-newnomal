# 카카오 OAuth 사용 예제

## 전체 플로우 예제

### 시나리오
학원 관리자가 "김철수" 학생에게 초대 링크를 보내고, 학생이 카카오 로그인으로 가입하는 과정

---

## 1. 관리자: 초대 링크 생성

### API 요청
```bash
POST http://localhost:8000/students/1/invite
Authorization: Bearer {admin_access_token}
```

### 응답
```json
{
  "student_id": 1,
  "student_name": "김철수",
  "invite_url": "http://localhost:8000/student/signup?token=xZY9k3mP...",
  "qr_url": "http://localhost:8000/student/qr/a1b2c3d4...",
  "expires_at": "2025-12-26T10:30:00"
}
```

### 관리자 액션
1. `invite_url`을 학부모 카카오톡으로 전송
2. 또는 QR 코드를 인쇄하여 제공

---

## 2. 학생/학부모: 초대 링크 클릭

### URL
```
http://localhost:8000/student/signup?token=xZY9k3mP...
```

### 서버 처리
1. 토큰 유효성 검사
   - 존재 여부 확인
   - 만료 시간 확인 (24시간)
   - 이미 사용되었는지 확인

2. State 토큰 생성 (CSRF 방지)
   ```python
   state_token = "abc123def456..."
   STATE_STORE[state_token] = {
       "invite_token": "xZY9k3mP...",
       "created_at": datetime.utcnow()
   }
   ```

3. 카카오 로그인으로 리다이렉트
   ```
   Location: /auth/kakao/start?state=abc123def456...
   ```

---

## 3. 카카오 OAuth 시작

### URL
```
http://localhost:8000/auth/kakao/start?state=abc123def456...
```

### 서버 처리
카카오 인증 서버로 리다이렉트:
```
Location: https://kauth.kakao.com/oauth/authorize
  ?client_id={KAKAO_REST_KEY}
  &redirect_uri=http://localhost:8000/auth/kakao/callback
  &response_type=code
  &state=abc123def456...
```

### 사용자 화면
- 카카오 로그인 페이지 표시
- 사용자가 카카오 ID/PW 입력
- (선택) 동의 항목 확인

---

## 4. 카카오 콜백

### 카카오에서 리다이렉트
```
http://localhost:8000/auth/kakao/callback
  ?code=vwxyz789...
  &state=abc123def456...
```

### 서버 처리

#### A. State 검증
```python
if state not in STATE_STORE:
    raise HTTPException(400, "유효하지 않은 state")

state_data = STATE_STORE[state]
invite_token = state_data["invite_token"]
del STATE_STORE[state]  # 1회성
```

#### B. 초대 토큰 재검증
```python
student = db.query(Student).filter(
    Student.invite_token == invite_token
).first()

if not student or student.invite_expires_at < now:
    raise HTTPException(400, "초대 링크 만료")
```

#### C. 인가 코드 → 액세스 토큰
```python
# POST https://kauth.kakao.com/oauth/token
response = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 21599,
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token_expires_in": 5183999
}
```

#### D. 액세스 토큰 → 사용자 정보
```python
# GET https://kapi.kakao.com/v2/user/me
# Authorization: Bearer {access_token}

response = {
    "id": 3456789012,  # 카카오 고유 ID (중요!)
    "connected_at": "2025-12-25T12:00:00Z",
    "kakao_account": {
        "profile": {
            "nickname": "김철수",
            "profile_image_url": "http://...",
            "thumbnail_image_url": "http://..."
        }
    }
}
```

#### E. DB 업데이트
```python
student.kakao_user_id = "3456789012"
student.invite_token = None  # 토큰 무효화
student.invite_expires_at = None
db.commit()
```

#### F. 성공 페이지로 리다이렉트
```
Location: /student/signup/success?studentId=1
```

---

## 5. 가입 완료

### URL
```
http://localhost:8000/student/signup/success?studentId=1
```

### 표시 내용
- ✅ 가입 완료 메시지
- 학생 이름: "김철수님"
- QR 코드 링크: `/student/qr/{qr_code}`

---

## 보안 플로우

### CSRF 공격 방지
```
초대 토큰 (invite_token) ─────┐
                              │
                              ▼
                        State 생성 (random)
                              │
                              ▼
                    카카오 왕복 동안 유지
                              │
                              ▼
                        State 검증 후 삭제 (1회성)
                              │
                              ▼
                    초대 토큰으로 학생 조회
```

### 토큰 무효화
```python
# 사용 전
student.invite_token = "xZY9k3mP..."
student.invite_expires_at = "2025-12-26T10:30:00"
student.kakao_user_id = None

# 사용 후
student.invite_token = None  # ← 재사용 불가
student.invite_expires_at = None
student.kakao_user_id = "3456789012"  # ← 연동 완료
```

---

## 에러 케이스

### 1. 만료된 초대 링크
```html
❌ 초대 링크가 만료되었습니다
초대 링크의 유효기간이 지났습니다. 관리자에게 새 링크를 요청하세요.
```

### 2. 이미 연동된 학생
```html
✅ 이미 가입 완료된 계정입니다
김철수님은 이미 카카오 계정과 연동되어 있습니다.
[내 QR 코드 보기]
```

### 3. 중복 카카오 계정
```python
# 카카오 ID 3456789012가 이미 다른 학생에게 연동됨
raise HTTPException(400, "이미 다른 학생에게 연동된 카카오 계정입니다")
```

### 4. 잘못된 State
```html
❌ 잘못된 접근입니다
인증 요청이 유효하지 않습니다. 처음부터 다시 시도해주세요.
```

---

## 데이터베이스 변경 사항

### Before (초대 링크 생성 전)
```sql
SELECT * FROM students WHERE id = 1;

id | name   | kakao_user_id | invite_token | invite_expires_at | qr_code
---|--------|---------------|--------------|-------------------|----------
1  | 김철수 | NULL          | NULL         | NULL              | a1b2c3d4
```

### After (초대 링크 생성 후)
```sql
id | name   | kakao_user_id | invite_token | invite_expires_at       | qr_code
---|--------|---------------|--------------|-------------------------|----------
1  | 김철수 | NULL          | xZY9k3mP...  | 2025-12-26 10:30:00    | a1b2c3d4
```

### After (가입 완료 후)
```sql
id | name   | kakao_user_id | invite_token | invite_expires_at | qr_code
---|--------|---------------|--------------|-------------------|----------
1  | 김철수 | 3456789012    | NULL         | NULL              | a1b2c3d4
```

---

## 테스트 시나리오

### ✅ 정상 플로우
1. 관리자가 초대 링크 생성
2. 학생이 링크 클릭
3. 카카오 로그인 성공
4. 가입 완료
5. QR 코드로 출석 체크 가능

### ⚠️ 만료 테스트
1. 초대 링크 생성
2. 24시간 대기 (또는 DB에서 `invite_expires_at` 과거로 변경)
3. 링크 클릭 → "만료됨" 오류

### ⚠️ 재사용 방지 테스트
1. 초대 링크로 가입 완료
2. 동일한 링크로 재접속 → "이미 가입 완료" 메시지

### ⚠️ 중복 카카오 계정 테스트
1. 학생 A가 카카오 계정 X로 가입
2. 학생 B의 초대 링크를 카카오 계정 X로 접속
3. "이미 다른 학생에게 연동된 계정" 오류

---

## 모니터링 포인트

### 로그 확인
```python
# 성공
print(f"✅ 학생 {student.name} (ID: {student.id}) 카카오 연동 완료")

# 실패
print(f"❌ 카카오 OAuth 실패: {error_message}")
```

### 메트릭
- 초대 링크 생성 수
- 가입 완료율
- 만료된 링크 접속 횟수
- OAuth 실패 횟수

### DB 쿼리
```sql
-- 연동 완료된 학생 수
SELECT COUNT(*) FROM students WHERE kakao_user_id IS NOT NULL;

-- 미연동 학생 수
SELECT COUNT(*) FROM students WHERE kakao_user_id IS NULL;

-- 대기 중인 초대 (만료 안 됨)
SELECT COUNT(*) FROM students 
WHERE invite_token IS NOT NULL 
AND invite_expires_at > NOW();
```

