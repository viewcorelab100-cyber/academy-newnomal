# 출석 체크 기능

## 📋 개요

학생들의 등원/하원을 체크하고 학부모에게 자동으로 카카오톡 알림을 발송하는 기능입니다.

---

## 🎯 핵심 규칙

### 1. 하루 1번 규칙
- **등원(IN)**: 하루에 1번만 가능
- **하원(OUT)**: 하루에 1번만 가능
- 이미 체크한 경우 버튼 비활성화

### 2. 자동 알림
- 등원/하원 체크 시 **자동으로 학부모에게 카카오톡 발송**
- 알림 실패해도 출석 체크는 완료됨

### 3. 간단한 로직
- 복잡한 통계나 차트 없음
- 버튼 클릭만으로 체크 완료
- 날짜별 조회 가능

---

## 🚀 API 엔드포인트

### 1. POST /attendance/check
**출석 체크 (등원/하원)**

```bash
curl -X POST "http://localhost:8000/attendance/check" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "type": "in"
  }'
```

**요청 Body:**
```json
{
  "student_id": 1,
  "type": "in"  // "in" 또는 "out"
}
```

**응답 (성공):**
```json
{
  "id": 1,
  "student_id": 1,
  "type": "in",
  "timestamp": "2024-01-15T09:00:00",
  "created_at": "2024-01-15T09:00:00"
}
```

**응답 (실패 - 이미 체크한 경우):**
```json
{
  "detail": "이미 오늘 등원 체크를 완료했습니다"
}
```

---

### 2. GET /attendance/
**출석 목록 조회 (날짜, 반 필터링)**

```bash
# 특정 날짜의 출석 기록
curl -X GET "http://localhost:8000/attendance/?date=2024-01-15" \
  -H "Authorization: Bearer {token}"

# 특정 반의 출석 기록
curl -X GET "http://localhost:8000/attendance/?class_id=1" \
  -H "Authorization: Bearer {token}"

# 특정 날짜 + 특정 반
curl -X GET "http://localhost:8000/attendance/?date=2024-01-15&class_id=1" \
  -H "Authorization: Bearer {token}"
```

**쿼리 파라미터:**
- `date`: 날짜 (YYYY-MM-DD 형식, 선택)
- `class_id`: 반 ID (선택)

**응답:**
```json
[
  {
    "id": 1,
    "student_id": 1,
    "type": "in",
    "timestamp": "2024-01-15T09:00:00",
    "created_at": "2024-01-15T09:00:00"
  },
  {
    "id": 2,
    "student_id": 1,
    "type": "out",
    "timestamp": "2024-01-15T18:00:00",
    "created_at": "2024-01-15T18:00:00"
  }
]
```

---

### 3. GET /attendance/student/{student_id}
**학생별 출석 기록 조회**

```bash
curl -X GET "http://localhost:8000/attendance/student/1" \
  -H "Authorization: Bearer {token}"
```

---

### 4. PATCH /attendance/{attendance_id}
**출석 기록 수정 (수동 보정)**

```bash
curl -X PATCH "http://localhost:8000/attendance/1" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "out",
    "timestamp": "2024-01-15T18:30:00"
  }'
```

**요청 Body:**
```json
{
  "type": "out",              // 선택
  "timestamp": "2024-01-15T18:30:00"  // 선택
}
```

**사용 케이스:**
- 등원 시간을 잘못 체크한 경우
- 수동으로 시간을 조정해야 하는 경우

---

## 🎨 HTML 페이지 (`/attendance-check`)

### 화면 구성

```
┌────────────────────────────────────────┐
│ ✅ 출석 체크                            │
│ 날짜: [2024-01-15] [조회] [오늘]       │
├────────────────────────────────────────┤
│ ┌──────────┐  ┌──────────┐            │
│ │ 김철수    │  │ 이영희    │            │
│ │ 서울고 고3│  │ 대치고 고2│            │
│ │[🏫등원]   │  │[🏫등원✓] │            │
│ │[🏠하원]   │  │[🏠하원]  │            │
│ │미체크     │  │등원 완료  │            │
│ └──────────┘  └──────────┘            │
└────────────────────────────────────────┘
```

### 기능

1. **날짜 선택**
   - 날짜 선택기로 특정 날짜 조회
   - "오늘" 버튼으로 빠르게 오늘 날짜로 이동

2. **학생 카드**
   - 모든 활성 학생 표시
   - 학생 이름, 학교, 학년 표시
   - 등원/하원 버튼

3. **출석 체크 버튼**
   - 🏫 등원 버튼 (녹색)
   - 🏠 하원 버튼 (주황색)
   - 이미 체크한 경우 버튼 비활성화 + ✓ 표시

4. **상태 표시**
   - 미체크: 회색
   - 등원 완료: 녹색
   - 하원만 체크됨: 주황색
   - 등원/하원 완료: 파란색

---

## 🔄 작동 흐름

### 등원 체크

```
1. 출석 체크 페이지 접속 (/attendance-check)
   ↓
2. 오늘 날짜의 학생 목록 로드
   ↓
3. "김철수" 학생의 "등원" 버튼 클릭
   ↓
4. 확인 다이얼로그 표시
   ↓
5. POST /attendance/check API 호출
   {
     "student_id": 1,
     "type": "in"
   }
   ↓
6. 서버에서 검증:
   - 오늘 이미 등원 체크했는지 확인
   - 없으면 DB에 저장
   ↓
7. 학부모에게 카카오톡 발송:
   "김철수 학생이 09:00에 등원했습니다"
   ↓
8. 화면 새로고침
   - "등원" 버튼 비활성화 + ✓ 표시
   - 상태: "등원 완료"
```

### 하원 체크

```
1. "김철수" 학생의 "하원" 버튼 클릭
   ↓
2. POST /attendance/check API 호출
   {
     "student_id": 1,
     "type": "out"
   }
   ↓
3. 학부모에게 카카오톡 발송:
   "김철수 학생이 18:00에 하원했습니다"
   ↓
4. 화면 새로고침
   - "하원" 버튼 비활성화 + ✓ 표시
   - 상태: "등원/하원 완료 ✓"
```

---

## 🔒 하루 1번 검증 로직

```python
# 오늘 날짜의 시작/끝
today_start = datetime.now().replace(hour=0, minute=0, second=0)
today_end = datetime.now().replace(hour=23, minute=59, second=59)

# 오늘 이미 같은 타입으로 체크했는지 확인
existing = db.query(Attendance).filter(
    Attendance.student_id == student_id,
    Attendance.type == type,  # "in" 또는 "out"
    Attendance.timestamp >= today_start,
    Attendance.timestamp <= today_end
).first()

if existing:
    raise HTTPException(400, "이미 오늘 등원 체크를 완료했습니다")
```

**동작:**
- 등원(IN)을 오전 9시에 체크하면, 같은 날 다시 등원 체크 불가
- 하원(OUT)은 별도로 1번 가능
- 다음 날이 되면 다시 체크 가능

---

## 📊 데이터베이스 스키마

```sql
CREATE TABLE attendances (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    type VARCHAR NOT NULL,  -- 'in' 또는 'out'
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 💡 사용 시나리오

### 시나리오 1: 정상적인 등원/하원

```
09:00 - 김철수 등원 체크 → 학부모에게 알림
18:00 - 김철수 하원 체크 → 학부모에게 알림
```

### 시나리오 2: 잘못 체크한 경우

```
09:00 - 김철수 등원 체크
09:05 - 실수로 하원 버튼 클릭 (실제로는 등원)
       → API 문서에서 PATCH /attendance/{id}로 수정
```

### 시나리오 3: 학생이 오지 않은 경우

```
- 등원 버튼 클릭 안 함
- 하원 버튼 클릭 안 함
- 상태: "미체크" 유지
```

---

## 🎯 입력 검증

### 서버 검증

1. **학생 존재 여부**
   ```python
   if not student:
       raise HTTPException(404, "학생을 찾을 수 없습니다")
   ```

2. **중복 체크 방지**
   ```python
   if existing_attendance:
       raise HTTPException(400, "이미 오늘 등원 체크를 완료했습니다")
   ```

3. **타입 검증** (Pydantic)
   ```python
   type: Literal["in", "out"]  # "in" 또는 "out"만 허용
   ```

---

## 🔧 수동 보정 (PATCH)

관리자가 잘못 체크한 출석 기록을 수정할 수 있습니다.

### 사용 예시

```bash
# 등원 시간을 9시에서 8시 30분으로 수정
curl -X PATCH "http://localhost:8000/attendance/1" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-01-15T08:30:00"
  }'

# 등원을 하원으로 변경
curl -X PATCH "http://localhost:8000/attendance/1" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "out"
  }'
```

**주의:**
- HTML UI에서는 제공하지 않음 (MVP)
- API 문서(`/docs`)에서만 수정 가능
- 수정해도 카카오톡은 재발송되지 않음

---

## 📱 카카오톡 알림

### 등원 알림

```
[학원명]
김철수 학생이 09:00에 등원했습니다.
```

### 하원 알림

```
[학원명]
김철수 학생이 18:00에 하원했습니다.
```

**발송 시점:**
- 출석 체크 버튼 클릭 즉시
- 백그라운드에서 자동 발송
- 실패해도 출석 체크는 완료

---

## 🚀 확장 가능성

현재는 최소 기능만 구현했지만, 나중에 추가 가능:

### 1. 통계 대시보드
```javascript
GET /attendance/stats?month=2024-01
// 월별 출석률 통계
```

### 2. 출석률 차트
```javascript
// 학생별 출석률
// 요일별 출석 패턴
// 월별 비교
```

### 3. 지각/조퇴 기능
```javascript
// 9시 이후 등원 → 지각
// 6시 이전 하원 → 조퇴
```

### 4. QR 코드 체크인
```javascript
// 학생이 QR 코드로 자동 체크
// 관리자 버튼 클릭 불필요
```

### 5. 자동 알림
```javascript
// 9시까지 등원 안 한 학생 자동 알림
// 6시 이후 하원 안 한 학생 알림
```

---

## 🎨 파일 구조

```
app/
├── api/
│   └── attendance.py        # API 엔드포인트
├── models/
│   └── attendance.py        # 데이터베이스 모델
├── schemas/
│   └── attendance.py        # Pydantic 스키마
└── templates/
    └── attendance.html      # 출석 체크 페이지
```

---

## 💡 사용 방법

### 1. 대시보드에서 "출석 체크" 클릭
http://localhost:8000/attendance-check

### 2. 날짜 선택 (기본: 오늘)
- 날짜 선택기로 특정 날짜 선택
- "오늘" 버튼으로 빠르게 이동

### 3. 학생의 등원/하원 버튼 클릭
- 등원: 녹색 버튼
- 하원: 주황색 버튼

### 4. 자동으로 학부모에게 알림 발송

### 5. 버튼 비활성화 + 상태 업데이트

---

## ✅ 요약

| 항목 | 내용 |
|------|------|
| **API** | POST /check, GET /, PATCH /{id} |
| **규칙** | 하루 1번 IN/OUT |
| **알림** | 자동 카카오톡 발송 |
| **UI** | 버튼 기반 (간단함) |
| **검증** | 중복 체크 방지 |
| **수정** | PATCH API로 가능 |
| **통계** | 없음 (MVP) |
| **차트** | 없음 (MVP) |

