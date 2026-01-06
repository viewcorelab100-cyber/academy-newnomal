# 카카오 OAuth 설정 가이드

## 문제: "Bad client credentials" 오류

카카오 로그인 동의 화면에서 "동의하고 계속하기"를 누르면 다음 오류가 발생합니다:
```json
{"detail":"카카오 토큰 발급 실패: Bad client credentials"}
```

### 원인
카카오 개발자 콘솔에서 **"Client Secret 사용"** 설정이 활성화되어 있는데, 애플리케이션 코드에서 `client_secret`을 제공하지 않아서 발생합니다.

---

## 해결 방법

### ✅ 방법 1: Client Secret 추가 (권장)

#### 1단계: 카카오 개발자 콘솔 접속
1. [카카오 개발자 콘솔](https://developers.kakao.com/) 접속
2. 앱 선택 → **내 애플리케이션** → 해당 앱 선택

#### 2단계: Client Secret 코드 확인
1. 좌측 메뉴에서 **제품 설정** → **카카오 로그인** → **보안** 클릭
2. **Client Secret** 섹션에서:
   - "Client Secret 코드"가 있는지 확인
   - "활성화 상태"가 **ON**으로 되어 있는지 확인
3. **Client Secret 코드 복사** (예: `abc123xyz...`)

#### 3단계: .env 파일에 추가
프로젝트 루트의 `.env` 파일을 열고 다음 줄을 수정:

```env
# Kakao OAuth
KAKAO_CLIENT_ID=53b8ba1e3b3edfb1157cecc2941f0e92
KAKAO_CLIENT_SECRET=여기에_복사한_Client_Secret_붙여넣기
KAKAO_REDIRECT_URI=http://localhost:8000/auth/student/kakao/callback
```

**예시:**
```env
KAKAO_CLIENT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

#### 4단계: 서버 재시작
```bash
# 서버를 재시작합니다
python run.py
```

---

### 🔧 방법 2: Client Secret 사용 비활성화 (대안)

Client Secret을 사용하지 않으려면:

1. 카카오 개발자 콘솔 → **제품 설정** → **카카오 로그인** → **보안**
2. "Client Secret 코드" 섹션에서 **활성화 상태를 OFF로 변경**
3. 저장 후 서버 재시작

⚠️ **주의**: 프로덕션 환경에서는 보안을 위해 **Client Secret 사용을 권장**합니다.

---

## Redirect URI 설정 확인

카카오 로그인이 작동하려면 **Redirect URI**가 올바르게 설정되어 있어야 합니다.

### 카카오 개발자 콘솔 설정
1. **제품 설정** → **카카오 로그인** → **Redirect URI**
2. 다음 URI들을 **모두 등록**:
   ```
   http://localhost:8000/auth/student/kakao/callback
   http://localhost:8000/auth/student/kakao/callback-existing
   ```

### 프로덕션 배포 시
프로덕션 도메인으로 배포할 때는:
```
https://yourdomain.com/auth/student/kakao/callback
https://yourdomain.com/auth/student/kakao/callback-existing
```

---

## 테스트 방법

1. 서버 실행:
   ```bash
   python run.py
   ```

2. 브라우저에서 접속:
   ```
   http://localhost:8000
   ```

3. **학생 로그인** 버튼 클릭

4. **카카오로 로그인** 버튼 클릭

5. 카카오 동의 화면에서 **동의하고 계속하기** 클릭

6. 성공 시: 학생 대시보드로 리다이렉트됩니다.

---

## 추가 트러블슈팅

### "redirect_uri mismatch" 오류
- 카카오 개발자 콘솔의 Redirect URI 설정 확인
- `.env`의 `KAKAO_REDIRECT_URI`와 일치하는지 확인

### "invalid_client" 오류
- `KAKAO_CLIENT_ID`가 올바른지 확인
- 카카오 개발자 콘솔의 **앱 키** → **REST API 키** 복사

### 서버 로그 확인
터미널에서 다음과 같은 로그를 확인할 수 있습니다:
```
🔑 Requesting Kakao Token with:
  - client_id: 53b8ba1e3b...
  - redirect_uri: http://localhost:8000/auth/student/kakao/callback
  - code: abc123xyz...
```

오류 발생 시:
```
❌ Kakao Token Error (401): {"error":"invalid_client","error_description":"Bad client credentials"}
```

---

## 관련 파일
- `app/auth/student.py`: 카카오 OAuth 로직
- `app/config.py`: 환경 변수 설정
- `.env`: 실제 키 값 저장 (보안상 .gitignore에 포함)



