# 학원 관리 시스템 MVP - 시스템 개요

## 아키텍처

### 기술 스택
- **Backend**: Python 3.9+ / FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Messaging**: KakaoTalk API (AlimTalk/FriendTalk)

### 데이터 모델

#### User (관리자)
- 이메일 기반 로그인
- JWT 토큰 인증
- 비밀번호 bcrypt 해싱

#### Student (학생)
- 기본 정보: 이름, 연락처, 학부모 연락처
- 학교/학년 정보
- 활성 상태 관리

#### Class (반)
- 반 이름, 과목, 담당 강사
- 수업 일정, 월 수강료
- 활성 상태 관리

#### Enrollment (수강)
- 학생-반 연결
- 수강 시작일/종료일
- 현재 수강 중 여부 추적

#### Attendance (출석)
- 등원(in) / 하원(out) 기록
- 타임스탬프
- 자동 카카오톡 알림

#### Invoice (청구서)
- 월별 자동 생성
- 납부 상태 (UNPAID/PAID)
- 납부 기한 관리

#### CounselingNote (상담 노트)
- 학생별 상담 내용
- 공개/비공개 설정
- SHARED 시 학부모에게 자동 알림

#### MessageLog (메시지 로그)
- 카카오톡 발송 이력
- 발송 상태 추적
- 에러 로그

## 주요 기능

### 1. 인증 시스템
- POST `/auth/register` - 관리자 계정 생성
- POST `/auth/login` - 로그인 (JWT 토큰 발급)
- GET `/auth/me` - 현재 사용자 정보

### 2. 학생 관리
- GET `/students` - 학생 목록
- POST `/students` - 학생 등록
- GET `/students/{id}` - 학생 상세
- PATCH `/students/{id}` - 학생 정보 수정
- DELETE `/students/{id}` - 학생 비활성화

### 3. 반 관리
- 학생 관리와 동일한 CRUD 패턴

### 4. 수강 관리
- 학생-반 등록
- 중복 수강 방지
- 수강 종료 처리

### 5. 출석 체크
- POST `/attendance/check` - 등원/하원 체크
- 자동 학부모 알림 (카카오톡)
- GET `/attendance/student/{id}` - 학생별 출석 기록

### 6. 청구/결제
- POST `/billing/run/{month}` - 월별 자동 청구 생성
- GET `/billing/invoices` - 청구서 목록
- PATCH `/billing/invoices/{id}` - 납부 처리
- POST `/billing/notify-overdue/{month}` - 미납자 알림

### 7. 상담 노트
- POST `/counseling/notes` - 상담 노트 작성
- SHARED 설정 시 자동 학부모 알림
- GET `/counseling/notes/student/{id}` - 학생별 상담 내역

### 8. 카카오톡 알림
- 출석 알림 (등원/하원)
- 청구서 발송 알림
- 미납 알림
- 상담 내용 공유 알림

## 시퀀스 다이어그램 구현

### 청구/결제 프로세스
1. 관리자가 `/billing/run/{month}` 호출
2. 시스템이 활성 수강생 조회
3. 청구서 자동 생성 (중복 방지)
4. 학부모에게 청구 알림 발송
5. 미납자 대상 `/billing/notify-overdue` 호출
6. 미납 알림 발송

### 상담 노트
1. 학생 상세에서 상담 메모 작성
2. POST `/counseling/notes` 호출
3. DB에 상담 노트 저장
4. visibility=SHARED인 경우 학부모에게 카카오톡 발송
5. 메시지 로그 기록

### 출석 체크
1. QR/RFID 등으로 학생 체크인/아웃
2. POST `/attendance/check` 호출
3. DB에 출석 레코드 저장
4. 학부모 연락처 조회
5. 카카오톡 알림 발송 (등원/하원 템플릿)
6. 메시지 로그 기록

## 보안

- JWT 토큰 기반 인증
- 모든 API는 인증 필요 (`get_current_user` 의존성)
- 비밀번호 bcrypt 해싱
- 환경 변수로 민감 정보 관리

## MVP 범위 밖
- 대시보드/차트
- AI 기능
- 분석 도구
- 학생/학부모용 로그인 (관리자만)
- 카카오 로그인

## 확장 가능성
- 학원별 커스터마이징 레이어 추가
- 결제 게이트웨이 연동
- 학부모 포털 (선택 사항)
- 모바일 앱 (API 재사용)

