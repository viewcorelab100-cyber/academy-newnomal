# 학생 관리 기능

## 📋 개요

학생의 기본 정보를 등록, 조회, 수정, 삭제할 수 있는 CRUD 기능입니다.

---

## 🎯 가정사항 (Assumptions)

### 1. 데이터 모델

**요구사항 (최소):**
- `id` - 학생 ID (자동 생성)
- `name` - 이름
- `phone` - 연락처
- `status` - 상태
- `createdAt` - 생성일

**실제 구현 (확장):**
```python
class Student:
    id: int                    # 자동 생성
    name: str                  # 필수
    phone: str                 # 선택 (학생 연락처)
    parent_phone: str          # 필수 (학부모 연락처, 카카오톡 알림용)
    school: str                # 선택
    grade: str                 # 선택
    notes: str                 # 선택 (메모)
    is_active: bool            # 상태 (True=활성, False=비활성)
    created_at: datetime       # 자동 생성
    updated_at: datetime       # 자동 업데이트
```

**이유:**
- 학원 관리에는 학부모 연락처가 필수 (카카오톡 알림 발송)
- 학교, 학년 정보가 필요함
- 메모로 특이사항 기록

---

### 2. 필수 필드

- ✅ `name` (이름) - 필수
- ✅ `parent_phone` (학부모 연락처) - 필수
- ❌ `phone` (학생 연락처) - 선택
- ❌ 나머지 - 선택

---

### 3. 삭제 방식

- 실제 DELETE가 아닌 **소프트 삭제** (Soft Delete)
- `is_active = False`로 설정
- 데이터는 영구 보존 (출석, 청구 등 관련 데이터 보존)

---

### 4. 페이지네이션 & 검색

- ❌ 페이지네이션 없음 (모든 학생 표시)
- ❌ 검색 기능 없음
- 이유: MVP 단계이므로 최소 기능만 구현

---

### 5. 입력 검증

**브라우저 (HTML5):**
- `required` 속성으로 필수 체크
- `pattern` 속성으로 전화번호 형식 체크

**서버 (FastAPI + Pydantic):**
- Pydantic 스키마로 자동 검증
- 타입 체크 (str, int, datetime 등)

---

## 🚀 API 엔드포인트

### 1. GET /students/
**학생 목록 조회**

```bash
curl -X GET "http://localhost:8000/students/" \
  -H "Authorization: Bearer {token}"
```

**응답:**
```json
[
  {
    "id": 1,
    "name": "김철수",
    "phone": "010-1234-5678",
    "parent_phone": "010-9876-5432",
    "school": "서울고등학교",
    "grade": "고3",
    "notes": "수학 특별 관리 필요",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": null
  }
]
```

---

### 2. POST /students/
**학생 등록**

```bash
curl -X POST "http://localhost:8000/students/" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김철수",
    "parent_phone": "010-9876-5432",
    "phone": "010-1234-5678",
    "school": "서울고등학교",
    "grade": "고3",
    "notes": "수학 특별 관리 필요"
  }'
```

**필수 필드:**
- `name`
- `parent_phone`

**선택 필드:**
- `phone`
- `school`
- `grade`
- `notes`

---

### 3. GET /students/{id}
**학생 상세 조회**

```bash
curl -X GET "http://localhost:8000/students/1" \
  -H "Authorization: Bearer {token}"
```

---

### 4. PATCH /students/{id}
**학생 정보 수정**

```bash
curl -X PATCH "http://localhost:8000/students/1" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김철수",
    "grade": "고3 (재수생)"
  }'
```

**특징:**
- 변경된 필드만 전송 가능
- `exclude_unset=True`로 처리

---

### 5. DELETE /students/{id}
**학생 삭제 (비활성화)**

```bash
curl -X DELETE "http://localhost:8000/students/1" \
  -H "Authorization: Bearer {token}"
```

**동작:**
- `is_active = False` 설정
- 데이터는 보존됨

---

## 🎨 HTML 페이지

### 1. 학생 목록 페이지 (`/students-list`)

**기능:**
- 모든 활성 학생 표시
- 테이블 형식 (이름, 학교, 학년, 연락처, 상태, 등록일)
- "학생 추가" 버튼
- 각 학생별 "수정", "삭제" 버튼

**화면 구성:**
```
┌─────────────────────────────────────┐
│  👨‍🎓 학생 관리         [+ 학생 추가]  │
├─────────────────────────────────────┤
│  이름  학교  학년  연락처  상태  등록일 │
│  김철수 서울고 고3  010-... [수정][삭제] │
│  이영희 대치고 고2  010-... [수정][삭제] │
└─────────────────────────────────────┘
```

---

### 2. 학생 추가/수정 페이지 (`/students/create`, `/students/edit/{id}`)

**기능:**
- 학생 정보 입력 폼
- 필수 필드 표시 (빨간 별표)
- 입력 검증 (형식, 필수 체크)
- 저장/취소 버튼

**화면 구성:**
```
┌─────────────────────────────┐
│  학생 추가/수정              │
├─────────────────────────────┤
│  이름 *: [          ]       │
│  학부모 연락처 *: [      ]  │
│  학생 연락처: [         ]   │
│  학교: [                ]   │
│  학년: [                ]   │
│  메모: [                ]   │
│         [취소]  [저장]      │
└─────────────────────────────┘
```

---

## 🔄 작동 흐름

### 학생 목록 조회

```
1. /students-list 접속
   ↓
2. localStorage에서 JWT 토큰 가져오기
   ↓
3. GET /students/ API 호출 (토큰 포함)
   ↓
4. 서버가 토큰 검증 → 학생 목록 반환
   ↓
5. JavaScript로 테이블 렌더링
```

---

### 학생 추가

```
1. "학생 추가" 버튼 클릭 → /students/create
   ↓
2. 폼에 정보 입력
   ↓
3. "저장" 버튼 클릭
   ↓
4. JavaScript로 입력 검증
   ↓
5. POST /students/ API 호출
   ↓
6. 서버가 DB에 저장
   ↓
7. 성공 → /students-list로 이동
```

---

### 학생 수정

```
1. "수정" 버튼 클릭 → /students/edit/1
   ↓
2. GET /students/1 API 호출 (기존 데이터 로드)
   ↓
3. 폼에 기존 데이터 표시
   ↓
4. 정보 수정 후 "저장"
   ↓
5. PATCH /students/1 API 호출
   ↓
6. 서버가 DB 업데이트
   ↓
7. 성공 → /students-list로 이동
```

---

### 학생 삭제

```
1. "삭제" 버튼 클릭
   ↓
2. 확인 다이얼로그 표시
   ↓
3. 확인 → DELETE /students/1 API 호출
   ↓
4. 서버가 is_active = False 설정
   ↓
5. 목록 새로고침
```

---

## 🔒 인증 & 보안

### 모든 API는 인증 필요

```python
@router.get("/students")
async def list_students(
    current_user: User = Depends(get_current_user)  # ← 인증 미들웨어
):
    # 로그인하지 않으면 401 Unauthorized
```

### 프론트엔드에서 토큰 전달

```javascript
fetch('/students/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

---

## 📊 데이터베이스 스키마

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    phone VARCHAR,
    parent_phone VARCHAR NOT NULL,
    school VARCHAR,
    grade VARCHAR,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

---

## 🎯 입력 검증

### HTML5 검증

```html
<!-- 필수 필드 -->
<input type="text" name="name" required>

<!-- 전화번호 형식 -->
<input 
    type="tel" 
    name="parent_phone" 
    pattern="[0-9]{2,3}-[0-9]{3,4}-[0-9]{4}"
    required
>
```

### JavaScript 검증

```javascript
if (!formData.name) {
    alert('이름을 입력해주세요');
    return;
}

if (!formData.parent_phone) {
    alert('학부모 연락처를 입력해주세요');
    return;
}
```

### 서버 검증 (Pydantic)

```python
class StudentCreate(BaseModel):
    name: str                     # 필수
    parent_phone: str             # 필수
    phone: Optional[str] = None   # 선택
    school: Optional[str] = None  # 선택
    grade: Optional[str] = None   # 선택
    notes: Optional[str] = None   # 선택
```

---

## 🚀 확장 가능성

현재는 최소 기능만 구현했지만, 나중에 추가 가능:

### 1. 페이지네이션
```javascript
GET /students/?skip=0&limit=20
```

### 2. 검색
```javascript
GET /students/?search=김철수
```

### 3. 필터링
```javascript
GET /students/?grade=고3&school=서울고
```

### 4. 정렬
```javascript
GET /students/?sort=name&order=asc
```

### 5. 대량 작업
- 엑셀 업로드/다운로드
- 대량 삭제
- 대량 메시지 발송

---

## 🎨 파일 구조

```
app/
├── api/
│   └── students.py          # API 엔드포인트
├── models/
│   └── student.py           # 데이터베이스 모델
├── schemas/
│   └── student.py           # Pydantic 스키마
└── templates/
    ├── students.html        # 학생 목록 페이지
    └── student-form.html    # 학생 추가/수정 페이지
```

---

## 💡 사용 방법

### 1. 서버 실행
```bash
uvicorn app.main:app --reload
```

### 2. 로그인
http://localhost:8000/login

### 3. 대시보드에서 "학생 관리" 클릭
http://localhost:8000/students-list

### 4. 학생 추가
- "+ 학생 추가" 버튼 클릭
- 정보 입력 후 저장

### 5. 학생 수정/삭제
- 목록에서 "수정" 또는 "삭제" 버튼 클릭

---

## 🔧 트러블슈팅

### 401 Unauthorized 에러
- 로그인이 만료됨
- 다시 로그인하세요

### 404 Not Found 에러
- 학생이 이미 삭제됨 (비활성화)
- 목록을 새로고침하세요

### 입력 검증 실패
- 필수 필드를 모두 입력했는지 확인
- 전화번호 형식: 010-1234-5678

---

## ✅ 요약

| 항목 | 내용 |
|------|------|
| **엔드포인트** | GET, POST, PATCH, DELETE /students |
| **필수 필드** | name, parent_phone |
| **삭제 방식** | Soft Delete (is_active=False) |
| **인증** | JWT 토큰 (모든 API) |
| **페이지** | 목록, 추가/수정 |
| **검증** | HTML5 + JavaScript + Pydantic |
| **페이지네이션** | 없음 (MVP) |
| **검색** | 없음 (MVP) |

