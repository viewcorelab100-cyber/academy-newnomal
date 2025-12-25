# QR 코드 자동 출석 시스템

## 📋 개요

학생이 QR 코드로 자동으로 출입을 체크할 수 있는 시스템입니다.
관리자의 수동 출석 체크와 병행하여 사용할 수 있습니다.

---

## 🎯 시스템 흐름

### 1단계: 관리자가 학생 초대

```
관리자 → 학생 등록 → "초대 링크 생성" 클릭
  ↓
시스템:
  - 고유한 invite_token 생성 (24시간 유효)
  - QR 코드용 고유 ID 생성
  - 초대 링크 생성
  ↓
관리자 → 초대 링크를 카카오톡으로 전송
```

**초대 링크 예시:**
```
http://localhost:8000/student/signup?token=abc123...
```

---

### 2단계: 학생이 카카오 로그인

```
학생 → 초대 링크 클릭
  ↓
학생 → "카카오 로그인" 버튼 클릭
  ↓
시스템:
  - 카카오 providerUserId 발급
  - student.kakao_user_id에 저장
  - invite_token 무효화
  ↓
학생 → QR 코드 페이지로 이동
```

**연동 데이터:**
```python
student.kakao_user_id = "kakao_abc123"  # 카카오 계정 ID
student.qr_code = "qr_def456"           # QR 코드용 고유 ID
```

---

### 3단계: QR 코드로 자동 체크인

```
학생 → 학원 입구 도착
  ↓
학생 → 스마트폰에서 QR 코드 표시
  ↓
관리자/입구 단말기 → QR 스캔
  ↓
시스템:
  - QR 코드에서 student_id 추출
  - 등원(IN) 또는 하원(OUT) 선택
  - 출석 기록 생성
  - 학부모에게 카카오톡 발송
  ↓
완료!
```

---

## 🔧 API 엔드포인트

### 1. POST /students/{student_id}/invite
**학생 초대 링크 생성 (관리자)**

```bash
curl -X POST "http://localhost:8000/students/1/invite" \
  -H "Authorization: Bearer {token}"
```

**응답:**
```json
{
  "student_id": 1,
  "student_name": "김철수",
  "invite_url": "http://localhost:8000/student/signup?token=abc123...",
  "qr_url": "http://localhost:8000/student/qr/qr_def456",
  "expires_at": "2024-12-26T10:00:00"
}
```

---

### 2. POST /student/signup
**학생 가입 (카카오 로그인)**

```bash
curl -X POST "http://localhost:8000/student/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "invite_token": "abc123...",
    "kakao_user_id": "kakao_xyz789"
  }'
```

**응답:**
```json
{
  "student_id": 1,
  "name": "김철수",
  "qr_code": "qr_def456",
  "message": "김철수님, 가입이 완료되었습니다!"
}
```

---

### 3. POST /student/checkin
**QR 코드로 자동 출석 체크**

```bash
curl -X POST "http://localhost:8000/student/checkin?qr_code=qr_def456&type=in" \
  -H "Content-Type: application/json"
```

**파라미터:**
- `qr_code`: QR 코드 (필수)
- `type`: "in" 또는 "out" (필수)

**응답 (성공):**
```json
{
  "success": true,
  "student_name": "김철수",
  "type": "등원",
  "timestamp": "2024-12-25 09:00",
  "message": "김철수님의 등원이 체크되었습니다!"
}
```

**응답 (실패 - 중복):**
```json
{
  "detail": "이미 오늘 등원 체크를 완료했습니다"
}
```

---

### 4. GET /student/info/{qr_code}
**QR 코드로 학생 정보 조회**

```bash
curl "http://localhost:8000/student/info/qr_def456"
```

**응답:**
```json
{
  "student_id": 1,
  "name": "김철수",
  "school": "서울고등학교",
  "grade": "고3",
  "is_connected": true
}
```

---

## 🎨 HTML 페이지

### 1. 관리자: 초대 링크 생성 (`/student-invite`)

**접근 방법:**
- 학생 목록 → "📱 초대하기" 링크 클릭

**기능:**
- 초대 링크 자동 생성
- QR 코드 표시
- 링크 복사 버튼
- 카카오톡 전송 버튼

**화면:**
```
┌──────────────────────────────┐
│ 📱 학생 초대 링크             │
├──────────────────────────────┤
│ 김철수                        │
│ ID: 1 | 만료: 12/26 10:00   │
│                              │
│ 초대 링크:                    │
│ [http://...token=abc123]     │
│ [📋 링크 복사하기]            │
│ [💬 카카오톡으로 보내기]      │
│                              │
│ QR 코드:                      │
│ [QR 이미지]                   │
│                              │
│ [← 학생 목록으로]             │
└──────────────────────────────┘
```

---

### 2. 학생: 가입 페이지 (`/student/signup`)

**접근 방법:**
- 초대 링크 클릭

**기능:**
- 카카오 로그인 버튼
- 자동 계정 연동
- QR 코드 페이지로 이동

**화면:**
```
┌──────────────────────────────┐
│ 🎓 학원 가입                  │
│                              │
│ 초대 링크를 통해 가입하시면   │
│ 자동 출석 체크 기능을         │
│ 사용할 수 있습니다            │
│                              │
│ [💬 카카오 로그인으로 3초 가입]│
│                              │
│ 📌 가입 후 이용 가능:         │
│ • QR 코드로 자동 출입 체크    │
│ • 학부모에게 자동 알림         │
│ • 출석 기록 확인              │
└──────────────────────────────┘
```

---

### 3. 학생: QR 코드 표시 (`/student/qr/{qr_code}`)

**접근 방법:**
- 가입 완료 후 자동 이동
- 또는 직접 URL 접속

**기능:**
- 학생 QR 코드 표시
- 출입 체크용

**화면:**
```
┌──────────────────────────────┐
│ 김철수                        │
│ 서울고등학교 고3              │
│                              │
│ ┌────────────────┐           │
│ │                │           │
│ │   QR CODE      │           │
│ │                │           │
│ └────────────────┘           │
│                              │
│ ✓ 카카오 계정 연동 완료       │
│                              │
│ 💡 사용 방법:                 │
│ 학원 입구의 QR 리더기에       │
│ 이 QR 코드를 스캔하면         │
│ 자동으로 출입이 체크됩니다!   │
│                              │
│ [📱 테스트: QR 스캔 시뮬레이션]│
└──────────────────────────────┘
```

---

### 4. 입구 단말기: QR 스캔 (`/qr-scan`)

**접근 방법:**
- QR 코드 스캔 후 자동 이동
- 또는 학원 입구 태블릿에서 상시 표시

**기능:**
- 등원/하원 버튼
- 즉시 출석 체크
- 결과 표시

**화면:**
```
┌──────────────────────────────┐
│ 🚪 출입 체크                  │
│                              │
│ 김철수 학생                   │
│                              │
│ ┌──────────┐  ┌──────────┐  │
│ │   🏫     │  │   🏠     │  │
│ │  등원    │  │  하원    │  │
│ └──────────┘  └──────────┘  │
│                              │
│ [✓ 등원 완료!]               │
│ 김철수님의 등원이             │
│ 체크되었습니다.               │
│ 시간: 2024-12-25 09:00       │
└──────────────────────────────┘
```

---

## 🔒 보안 & 검증

### 1. 초대 토큰 만료
```python
invite_expires_at = datetime.utcnow() + timedelta(hours=24)

if datetime.utcnow() > student.invite_expires_at:
    raise HTTPException(400, "초대 링크가 만료되었습니다")
```

### 2. 중복 연동 방지
```python
if student.kakao_user_id:
    raise HTTPException(400, "이미 연동된 학생입니다")
```

### 3. 하루 1번 출석 체크
```python
# 오늘 이미 체크했는지 확인
if existing_attendance:
    raise HTTPException(400, "이미 오늘 등원 체크를 완료했습니다")
```

---

## 🎯 데이터베이스 스키마 변경

```sql
ALTER TABLE students ADD COLUMN kakao_user_id VARCHAR UNIQUE;
ALTER TABLE students ADD COLUMN invite_token VARCHAR UNIQUE;
ALTER TABLE students ADD COLUMN invite_expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE students ADD COLUMN qr_code VARCHAR UNIQUE;
```

---

## 📱 카카오 로그인 (MVP vs 프로덕션)

### MVP (현재 구현)
```javascript
// 시뮬레이션
const kakaoUserId = 'kakao_' + Math.random().toString(36).substr(2, 9);
```

### 프로덕션 (실제 환경)
```javascript
// 카카오 SDK 사용
Kakao.Auth.login({
  success: function(authObj) {
    const kakaoUserId = authObj.access_token;
    // 백엔드로 전송
  }
});
```

**필요한 것:**
- 카카오 개발자 계정
- 카카오 앱 등록
- REST API 키
- JavaScript SDK

---

## 🔄 전체 플로우 정리

```
[관리자]
1. 학생 등록 (이름, 학부모 연락처 등)
   ↓
2. "📱 초대하기" 클릭
   ↓
3. 초대 링크 생성
   ↓
4. 카카오톡으로 링크 전송

[학생]
5. 초대 링크 클릭
   ↓
6. 카카오 로그인
   ↓
7. 자동 연동 완료
   ↓
8. QR 코드 저장 (스마트폰)

[출입 체크]
9. 학원 입구 도착
   ↓
10. QR 코드 스캔
   ↓
11. 등원/하원 선택
   ↓
12. 자동 출석 체크
   ↓
13. 학부모에게 카카오톡 발송
```

---

## 💡 사용 시나리오

### 시나리오 1: 신규 학생 등록
```
1. 관리자: 학생 등록 (김철수)
2. 관리자: "초대하기" → 링크 복사 → 카카오톡 전송
3. 김철수: 링크 클릭 → 카카오 로그인
4. 시스템: 연동 완료 → QR 코드 표시
5. 김철수: QR 코드 스크린샷 저장
```

### 시나리오 2: 출입 체크
```
1. 김철수: 학원 도착 (09:00)
2. 김철수: QR 코드 표시
3. 입구 태블릿: QR 스캔 → "등원" 버튼 자동 인식
4. 시스템: 출석 기록 생성
5. 학부모: 카카오톡 수신 "김철수 학생이 09:00에 등원했습니다"
```

### 시나리오 3: 중복 체크 방지
```
1. 김철수: 09:00에 등원 체크
2. 김철수: 09:05에 다시 QR 스캔 시도
3. 시스템: "이미 오늘 등원 체크를 완료했습니다" 에러
4. 화면: 에러 메시지 표시
```

---

## 🎨 장점

### 1. UX 좋음
- 학생이 직접 체크 가능
- 관리자 부담 감소
- 빠른 출입 처리

### 2. 정확도 높음
- 학생별 고유 QR 코드
- 카카오 계정 연동으로 신원 확인
- 중복 체크 방지

### 3. 운영 편함
- 초대 링크 한 번만 전송
- 영구적으로 사용 가능
- 추가 비용 없음

---

## 🚀 확장 가능성

### 1. NFC 태그
```javascript
// QR 코드 대신 NFC 카드 사용
student.nfc_id = "nfc_abc123"
```

### 2. 안면 인식
```javascript
// QR 코드 없이 얼굴로 인식
student.face_id = "face_def456"
```

### 3. 위치 기반 체크인
```javascript
// GPS로 학원 근처에 있을 때만 체크 가능
if (distance > 100) {
  throw new Error("학원 근처에서만 체크 가능합니다");
}
```

---

## ✅ 요약

| 항목 | 내용 |
|------|------|
| **방식** | 초대 링크 + 카카오 로그인 |
| **장점** | 정확도 최고, 운영 편함 |
| **초대** | 24시간 유효 |
| **QR** | 학생별 고유 코드 |
| **출입** | 하루 IN/OUT 각 1번 |
| **알림** | 자동 카카오톡 발송 |
| **관리** | 수동 + 자동 병행 가능 |

