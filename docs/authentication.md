# 인증 시스템 구조

## 🔐 인증 방식: JWT (JSON Web Token)

### 왜 JWT를 선택했나요?

**Session 방식:**
```
장점: 서버에서 완전한 제어 가능
단점: 서버에 세션 저장 필요 (메모리/DB 사용)
     여러 서버로 확장 시 세션 동기화 필요
```

**JWT 방식:** ✅ 선택!
```
장점: 서버가 상태를 저장하지 않음 (Stateless)
     여러 서버로 쉽게 확장 가능
     모바일 앱과 쉽게 연동
     토큰에 사용자 정보 포함 가능
단점: 토큰이 탈취되면 만료까지 무효화 불가
     토큰 크기가 세션 ID보다 큼
```

---

## 📋 구현된 API 엔드포인트

### 1. POST /auth/login
**요청:**
```json
{
  "email": "admin@academy.com",
  "password": "admin123"
}
```

**응답 (성공):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**응답 (실패):**
```json
{
  "detail": "이메일 또는 비밀번호가 올바르지 않습니다"
}
```

---

### 2. GET /auth/me
**요청 헤더:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**응답:**
```json
{
  "id": 1,
  "email": "admin@academy.com",
  "full_name": "관리자",
  "is_active": true,
  "is_superuser": false
}
```

---

## 🔧 구현 구조

### 1. API 라우트 핸들러 (`app/api/auth.py`)

```python
@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # 1. 이메일/비밀번호로 사용자 인증
    user = authenticate_user(db, user_data.email, user_data.password)
    
    # 2. 인증 실패 시 401 에러
    if not user:
        raise HTTPException(status_code=401, detail="인증 실패")
    
    # 3. JWT 토큰 생성 (사용자 이메일 포함)
    access_token = create_access_token(data={"sub": user.email})
    
    # 4. 토큰 반환
    return {"access_token": access_token, "token_type": "bearer"}
```

---

### 2. 인증 미들웨어 (`app/services/auth.py`)

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    # 1. Authorization 헤더에서 토큰 추출
    token = credentials.credentials
    
    # 2. JWT 토큰 검증 및 디코딩
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")
    
    # 3. 이메일로 사용자 조회
    user = db.query(User).filter(User.email == email).first()
    
    # 4. 사용자 반환
    return user
```

**사용 예시:**
```python
@router.get("/students")
async def list_students(
    current_user: User = Depends(get_current_user)  # ← 인증 필요!
):
    # current_user는 로그인한 사용자 정보
    return students
```

---

### 3. HTML 로그인 폼 (`app/templates/login.html`)

**핵심 JavaScript 코드:**
```javascript
// 1. 로그인 API 호출
const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
});

const data = await response.json();

// 2. 토큰을 localStorage에 저장
localStorage.setItem('access_token', data.access_token);

// 3. 대시보드로 이동
window.location.href = '/dashboard';
```

**API 호출 시 토큰 사용:**
```javascript
const token = localStorage.getItem('access_token');

fetch('/auth/me', {
    headers: {
        'Authorization': `Bearer ${token}`  // ← 토큰 포함!
    }
});
```

---

## 🔒 보호된 라우트 예시

### 인증이 필요한 API

```python
# app/api/students.py
@router.get("/students")
async def list_students(
    current_user: User = Depends(get_current_user)  # ← 인증 미들웨어
):
    # 로그인하지 않으면 401 에러!
    return students
```

### 인증이 필요 없는 API

```python
# app/main.py
@app.get("/")
async def root():
    # 누구나 접근 가능
    return "Hello World"
```

---

## 📊 인증 흐름도

```
1. 로그인 페이지 접속
   ↓
2. 이메일/비밀번호 입력
   ↓
3. POST /auth/login → JWT 토큰 발급
   ↓
4. 토큰을 localStorage에 저장
   ↓
5. 대시보드 접속
   ↓
6. GET /auth/me (토큰 포함) → 사용자 정보 확인
   ↓
7. 모든 API 호출 시 토큰 포함
   ↓
8. 로그아웃 → localStorage에서 토큰 삭제
```

---

## 🎯 보안 고려사항

### 1. 비밀번호 암호화
```python
# bcrypt로 비밀번호 해시
hashed = get_password_hash("admin123")
# → $2b$12$abc...xyz (복호화 불가능)
```

### 2. JWT 토큰 만료 시간
```python
# config.py
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8시간
```

### 3. HTTPS 사용 (프로덕션)
```
⚠️ 프로덕션 환경에서는 반드시 HTTPS 사용!
HTTP는 토큰이 평문으로 전송됨
```

### 4. CORS 설정
```python
# 프로덕션에서는 특정 도메인만 허용
allow_origins=["https://yourdomain.com"]
```

---

## 🚀 사용자 생성 (수동)

관리자는 UI가 없으므로 수동으로 생성:

### 방법 1: 초기화 스크립트
```bash
python scripts/init_db.py
# → admin@academy.com / admin123 생성됨
```

### 방법 2: API 문서에서 생성
1. http://localhost:8000/docs 접속
2. POST /auth/register 찾기
3. "Try it out" 클릭
4. 사용자 정보 입력 후 Execute

### 방법 3: Python 콘솔
```python
from app.database import SessionLocal
from app.models.user import User
from app.services.auth import get_password_hash

db = SessionLocal()
user = User(
    email="newadmin@academy.com",
    hashed_password=get_password_hash("password123"),
    full_name="새 관리자"
)
db.add(user)
db.commit()
```

---

## 📝 요약

| 항목 | 설명 |
|------|------|
| **인증 방식** | JWT (JSON Web Token) |
| **토큰 저장** | localStorage (브라우저) |
| **토큰 전달** | Authorization: Bearer {token} |
| **비밀번호** | bcrypt 해시 (복호화 불가) |
| **만료 시간** | 8시간 (480분) |
| **보호 방식** | `Depends(get_current_user)` |
| **등록 UI** | 없음 (수동 생성) |

---

## 🎨 프론트엔드 확장

현재는 순수 HTML + JavaScript이지만, 나중에 React/Vue로 교체 가능:

```javascript
// React 예시
const token = localStorage.getItem('access_token');

axios.get('/api/students', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => setStudents(res.data));
```

API는 동일하게 사용 가능! 🚀

