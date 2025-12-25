# 카카오 OAuth 연동 가이드

## 개요
학생이 초대 링크를 통해 카카오 로그인으로 가입하는 OAuth 플로우가 구현되었습니다.

## 플로우 설명

### 1단계: 관리자가 초대 링크 생성
```
POST /students/{student_id}/invite
```
- 학생별 고유한 초대 토큰 생성 (24시간 유효)
- 초대 URL: `http://localhost:8000/student/signup?token={invite_token}`

### 2단계: 학생이 초대 링크 클릭
```
GET /student/signup?token={invite_token}
```
- 초대 토큰 유효성 검사
- CSRF 방지를 위한 state 토큰 생성
- 카카오 로그인 페이지로 리다이렉트

### 3단계: 카카오 로그인
```
GET /auth/kakao/start?state={state_token}
```
- 카카오 인증 서버로 리다이렉트
- 사용자가 카카오 로그인 수행

### 4단계: 카카오 콜백
```
GET /auth/kakao/callback?code={code}&state={state}
```
- 인가 코드를 액세스 토큰으로 교환
- 카카오 사용자 정보 조회 (kakao_user_id)
- DB에 학생 정보 업데이트 (카카오 계정 연동)
- 초대 토큰 무효화 (1회성)

### 5단계: 가입 완료
```
GET /student/signup/success?studentId={student_id}
```
- 가입 완료 메시지 표시
- QR 코드 페이지 링크 제공

## 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# Database
DATABASE_URL=sqlite:///./academy.db

# JWT 설정
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# 카카오 OAuth 설정 (필수)
KAKAO_REST_KEY=your_kakao_rest_api_key_here
KAKAO_CLIENT_SECRET=  # 선택사항
KAKAO_REDIRECT_URI=http://localhost:8000/auth/kakao/callback

# 애플리케이션 설정
BASE_URL=http://localhost:8000
```

## 카카오 개발자 콘솔 설정

### 1. 카카오 개발자 콘솔 접속
https://developers.kakao.com/console

### 2. 애플리케이션 생성
1. "내 애플리케이션" → "애플리케이션 추가하기"
2. 앱 이름 입력 (예: "학원 관리 시스템")
3. 앱 아이콘 업로드 (선택사항)

### 3. 앱 키 확인
"내 애플리케이션" → "앱 설정" → "앱 키"
- **REST API 키**를 복사하여 `.env` 파일의 `KAKAO_REST_KEY`에 입력

### 4. 플랫폼 설정
"내 애플리케이션" → "앱 설정" → "플랫폼"
1. "Web 플랫폼 등록" 클릭
2. 사이트 도메인 입력:
   - 개발: `http://localhost:8000`
   - 프로덕션: `https://yourdomain.com`

### 5. 카카오 로그인 활성화
"내 애플리케이션" → "제품 설정" → "카카오 로그인"
1. "카카오 로그인 활성화" ON
2. "Redirect URI 등록" 클릭
   - 개발: `http://localhost:8000/auth/kakao/callback`
   - 프로덕션: `https://yourdomain.com/auth/kakao/callback`

### 6. 동의 항목 설정 (선택사항)
"제품 설정" → "카카오 로그인" → "동의항목"
- 필수: 없음 (기본 정보만 사용)
- 선택: 프로필 정보, 카카오계정(이메일) 등

## 보안 고려사항

### 1. State 파라미터
- CSRF 공격 방지를 위해 state 토큰 사용
- 현재: 메모리에 임시 저장 (개발용)
- 프로덕션: Redis 또는 DB에 저장 권장

### 2. HTTPS 사용
프로덕션 환경에서는 반드시 HTTPS 사용:
```env
BASE_URL=https://yourdomain.com
KAKAO_REDIRECT_URI=https://yourdomain.com/auth/kakao/callback
```

### 3. Client Secret 사용 (권장)
카카오 개발자 콘솔에서 "보안" → "코드 인증" 설정:
1. "Client Secret" 발급
2. `.env`에 `KAKAO_CLIENT_SECRET` 추가
3. "상태" ON으로 변경

### 4. 초대 토큰 만료
- 기본: 24시간
- 필요시 `app/api/student_invite.py`에서 조정 가능

## 데이터베이스 스키마

### Student 모델
```python
class Student(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    parent_phone = Column(String, nullable=False)
    
    # 카카오 연동 필드
    kakao_user_id = Column(String, unique=True, nullable=True)  # 카카오 ID
    invite_token = Column(String, unique=True, nullable=True)   # 초대 토큰
    invite_expires_at = Column(DateTime, nullable=True)         # 만료 시간
    qr_code = Column(String, unique=True, nullable=True)        # QR 코드
```

## API 엔드포인트

### 관리자용 (인증 필요)
- `POST /students/{student_id}/invite` - 초대 링크 생성
- `GET /students/{student_id}/invite-status` - 초대 상태 조회

### 학생용 (인증 불필요)
- `GET /student/signup?token={token}` - 초대 링크 진입
- `GET /auth/kakao/start?state={state}` - 카카오 로그인 시작
- `GET /auth/kakao/callback?code={code}&state={state}` - 카카오 콜백
- `GET /student/signup/success?studentId={id}` - 가입 완료

### QR 코드
- `GET /student/qr/{qr_code}` - 학생 QR 코드 표시
- `POST /student/checkin?qr_code={code}&type={in|out}` - QR 출석 체크

## 테스트 방법

### 1. 서버 실행
```bash
# Windows
start.bat

# Linux/Mac
uvicorn app.main:app --reload
```

### 2. 관리자 로그인
- http://localhost:8000/login
- 기본 계정으로 로그인

### 3. 학생 초대 링크 생성
1. http://localhost:8000/students-list
2. 학생 선택
3. "초대 링크 생성" 버튼 클릭
4. 생성된 링크 복사

### 4. 학생 가입 테스트
1. 새 브라우저/시크릿 모드에서 초대 링크 열기
2. 카카오 로그인 진행
3. 가입 완료 페이지 확인
4. QR 코드 페이지 확인

## 문제 해결

### 오류: "Invalid client_id"
- `.env` 파일의 `KAKAO_REST_KEY` 확인
- 카카오 개발자 콘솔에서 REST API 키 재확인

### 오류: "Invalid redirect_uri"
- `.env`의 `KAKAO_REDIRECT_URI` 확인
- 카카오 개발자 콘솔의 Redirect URI 등록 확인
- 프로토콜(http/https), 도메인, 포트가 정확히 일치해야 함

### 오류: "유효하지 않은 초대 링크"
- 초대 링크가 24시간 이내인지 확인
- 이미 사용된 토큰은 재사용 불가
- 새 초대 링크 생성 필요

### 오류: "이미 연동된 학생"
- 해당 학생은 이미 카카오 계정과 연동됨
- DB에서 `kakao_user_id` 초기화 후 재시도 가능

## 프로덕션 배포 체크리스트

- [ ] HTTPS 설정 완료
- [ ] 환경 변수 프로덕션 값으로 변경
- [ ] 카카오 개발자 콘솔에 프로덕션 도메인 등록
- [ ] Client Secret 활성화
- [ ] State 저장소를 Redis로 변경
- [ ] 로깅 및 모니터링 설정
- [ ] 에러 처리 강화
- [ ] Rate limiting 설정

