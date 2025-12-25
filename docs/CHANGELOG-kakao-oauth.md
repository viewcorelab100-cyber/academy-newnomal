# 카카오 OAuth 연동 변경 사항

## 📅 날짜: 2025-12-25

## 🎯 목적
학생이 초대 링크를 통해 카카오 로그인으로 간편하게 가입하고, QR 코드로 출석 체크할 수 있도록 OAuth 플로우 구현

---

## ✨ 새로운 기능

### 1. 카카오 OAuth 2.0 인증 플로우
- **Authorization Code Grant** 방식 구현
- CSRF 공격 방지를 위한 state 파라미터 사용
- 1회성 초대 토큰 시스템 (24시간 유효)

### 2. 보안 강화
- State 토큰 (랜덤 생성) + 초대 토큰 분리
- 토큰 재사용 방지 (사용 후 자동 무효화)
- 중복 카카오 계정 연동 차단
- 만료 시간 검증

### 3. 사용자 경험 개선
- 직관적인 오류 메시지 (HTML 페이지)
- 가입 완료 후 바로 QR 코드 페이지로 이동
- 이미 가입된 경우 안내 메시지

---

## 📝 변경된 파일

### 새로 추가된 파일
1. **`app/api/kakao_oauth.py`** (신규)
   - 카카오 OAuth 전체 플로우 처리
   - 4개 엔드포인트:
     - `GET /student/signup?token=...`
     - `GET /auth/kakao/start?state=...`
     - `GET /auth/kakao/callback?code=...&state=...`
     - `GET /student/signup/success?studentId=...`

2. **`docs/kakao-oauth-setup.md`** (신규)
   - 카카오 개발자 콘솔 설정 가이드
   - 환경 변수 설정 방법
   - 보안 고려사항
   - 문제 해결 가이드

3. **`docs/kakao-oauth-example.md`** (신규)
   - 전체 플로우 예제 (5단계)
   - API 요청/응답 샘플
   - DB 변경 사항
   - 테스트 시나리오

4. **`docs/CHANGELOG-kakao-oauth.md`** (신규)
   - 변경 사항 요약

### 수정된 파일

1. **`app/config.py`**
   ```python
   # 추가된 환경 변수
   KAKAO_REST_KEY: str
   KAKAO_CLIENT_SECRET: Optional[str]
   KAKAO_REDIRECT_URI: str
   BASE_URL: str
   ```

2. **`app/services/kakao.py`**
   ```python
   # 추가된 메서드
   async def get_kakao_access_token(code: str) -> dict
   async def get_kakao_user_info(access_token: str) -> dict
   ```

3. **`app/main.py`**
   ```python
   # 새 라우터 등록
   app.include_router(kakao_oauth.router)
   
   # 제거된 라우트
   # GET /student/signup (이제 kakao_oauth.py에서 처리)
   ```

4. **`README.md`**
   - 카카오 OAuth 기능 설명 추가
   - 환경 변수 설정 가이드 추가
   - 새 API 엔드포인트 문서화

---

## 🔄 데이터 플로우

```
[관리자]
    │
    ▼
 초대 링크 생성
    │
    ▼
[학생/학부모]
    │
    ▼
 초대 링크 클릭
    │
    ├─ 토큰 검증
    ├─ State 생성
    └─ 카카오 로그인
         │
         ▼
      [카카오]
         │
         ├─ 사용자 인증
         └─ 인가 코드 발급
              │
              ▼
         [서버 콜백]
              │
              ├─ State 검증
              ├─ 인가 코드 → 액세스 토큰
              ├─ 액세스 토큰 → 사용자 정보
              ├─ DB 업데이트 (카카오 ID 저장)
              └─ 토큰 무효화
                   │
                   ▼
              [가입 완료]
                   │
                   └─ QR 코드 발급
```

---

## 🔐 보안 개선 사항

### 1. CSRF 방지
```python
# Before: 초대 토큰을 state에 직접 사용 (취약)
state = invite_token  # ❌

# After: 랜덤 state + 서버에서 매핑
state = secrets.token_urlsafe(32)  # ✅
STATE_STORE[state] = {"invite_token": invite_token}
```

### 2. 토큰 재사용 방지
```python
# 가입 완료 시 자동 무효화
student.invite_token = None
student.invite_expires_at = None
```

### 3. 중복 연동 차단
```python
# 같은 카카오 계정으로 여러 학생 연동 불가
existing = db.query(Student).filter(
    Student.kakao_user_id == kakao_user_id
).first()

if existing:
    raise HTTPException(400, "이미 연동된 카카오 계정")
```

---

## 🗄️ 데이터베이스 스키마

### Student 테이블 (기존)
```python
class Student(Base):
    # ... 기존 필드 ...
    
    # 카카오 연동 필드 (이미 존재함)
    kakao_user_id = Column(String, unique=True, nullable=True)
    invite_token = Column(String, unique=True, nullable=True)
    invite_expires_at = Column(DateTime, nullable=True)
    qr_code = Column(String, unique=True, nullable=True)
```

**변경 사항:** 없음 (기존 스키마 활용)

---

## 🚀 배포 전 체크리스트

### 필수 설정
- [ ] `.env` 파일에 카카오 REST API 키 설정
- [ ] 카카오 개발자 콘솔에 Redirect URI 등록
- [ ] 카카오 로그인 활성화

### 프로덕션 환경
- [ ] HTTPS 적용
- [ ] BASE_URL을 실제 도메인으로 변경
- [ ] KAKAO_REDIRECT_URI를 HTTPS로 변경
- [ ] Client Secret 활성화 권장
- [ ] State 저장소를 Redis로 변경 권장
- [ ] 로깅 및 모니터링 설정

### 테스트
- [ ] 정상 가입 플로우 테스트
- [ ] 만료된 링크 테스트
- [ ] 재사용 방지 테스트
- [ ] 중복 계정 테스트
- [ ] QR 코드 출석 체크 테스트

---

## 📊 기대 효과

### 사용자 편의성
- ✅ 이메일/비밀번호 없이 카카오로 간편 가입
- ✅ QR 코드로 빠른 출석 체크
- ✅ 학부모에게 자동 알림 발송

### 관리 효율성
- ✅ 초대 링크 1회 생성으로 가입 완료
- ✅ 수동 계정 생성 불필요
- ✅ 카카오 ID로 학생 고유 식별

### 보안
- ✅ OAuth 2.0 표준 프로토콜
- ✅ CSRF 공격 방지
- ✅ 토큰 재사용 불가
- ✅ 만료 시간 관리

---

## 🔧 개발 환경 테스트

### 1. 환경 변수 설정
```bash
# .env 파일 생성
KAKAO_REST_KEY=your_test_key
KAKAO_REDIRECT_URI=http://localhost:8000/auth/kakao/callback
BASE_URL=http://localhost:8000
```

### 2. 서버 실행
```bash
uvicorn app.main:app --reload
```

### 3. 초대 링크 생성
```bash
# 관리자 로그인 후
curl -X POST "http://localhost:8000/students/1/invite" \
  -H "Authorization: Bearer {token}"
```

### 4. 브라우저에서 테스트
1. 초대 링크 열기
2. 카카오 로그인 진행
3. 가입 완료 확인
4. QR 코드 페이지 확인

---

## 📞 문제 해결

### 자주 발생하는 오류

**1. "Invalid client_id"**
- 원인: KAKAO_REST_KEY가 잘못됨
- 해결: 카카오 개발자 콘솔에서 REST API 키 재확인

**2. "Invalid redirect_uri"**
- 원인: Redirect URI가 등록되지 않음
- 해결: 카카오 개발자 콘솔에서 정확한 URI 등록

**3. "유효하지 않은 state"**
- 원인: State가 만료되거나 서버 재시작
- 해결: 초대 링크부터 다시 시작

**4. "초대 링크 만료"**
- 원인: 24시간 경과
- 해결: 관리자가 새 초대 링크 생성

---

## 🎓 학습 자료

### 공식 문서
- [카카오 로그인 REST API](https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [FastAPI 문서](https://fastapi.tiangolo.com/)

### 프로젝트 문서
- [kakao-oauth-setup.md](kakao-oauth-setup.md) - 설정 가이드
- [kakao-oauth-example.md](kakao-oauth-example.md) - 플로우 예제
- [qr-attendance.md](qr-attendance.md) - QR 출석 체크

---

## 👥 기여자
- 개발: AI Assistant 🐙
- 요청: 이현수

---

## 📋 다음 단계

### 단기 (1주 이내)
- [ ] 프로덕션 환경 배포
- [ ] 실제 사용자 테스트
- [ ] 피드백 수집

### 중기 (1개월 이내)
- [ ] State 저장소를 Redis로 마이그레이션
- [ ] 로깅 및 모니터링 대시보드 구축
- [ ] 사용자 가이드 비디오 제작

### 장기 (3개월 이내)
- [ ] 다른 OAuth 제공자 추가 (네이버, Google)
- [ ] 학생 전용 모바일 앱 개발
- [ ] QR 코드 자동 생성/인쇄 기능

