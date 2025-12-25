from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, students, classes, enrollments, attendance, billing, counseling, student_invite, student_auth, kakao_oauth
from app.database import Base, engine

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="학원 관리 시스템 MVP",
    description="소규모 입시학원을 위한 경량 관리 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API 라우터 등록
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(student_invite.router)
app.include_router(student_auth.router)
app.include_router(kakao_oauth.router)  # 카카오 OAuth 플로우
app.include_router(classes.router)
app.include_router(enrollments.router)
app.include_router(attendance.router)
app.include_router(billing.router)
app.include_router(counseling.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """메인 페이지"""
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """로그인 페이지"""
    with open("app/templates/login.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """대시보드 페이지"""
    with open("app/templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/students-list", response_class=HTMLResponse)
async def students_list_page():
    """학생 목록 페이지"""
    with open("app/templates/students.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/students-create", response_class=HTMLResponse)
async def student_create_page():
    """학생 추가 페이지"""
    with open("app/templates/student-form.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/students-edit/{student_id}", response_class=HTMLResponse)
async def student_edit_page(student_id: int):
    """학생 수정 페이지"""
    with open("app/templates/student-form.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/attendance-check", response_class=HTMLResponse)
async def attendance_check_page():
    """출석 체크 페이지"""
    with open("app/templates/attendance.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/student-invite", response_class=HTMLResponse)
async def student_invite_page():
    """학생 초대 페이지"""
    with open("app/templates/student-invite.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/student/qr/{qr_code}", response_class=HTMLResponse)
async def student_qr_page(qr_code: str):
    """학생 QR 코드 페이지"""
    with open("app/templates/student-qr.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/qr-scan", response_class=HTMLResponse)
async def qr_scan_page():
    """QR 스캔 페이지"""
    with open("app/templates/qr-scan.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "ok", "message": "학원 관리 시스템이 정상 작동 중입니다"}

