"""
FastAPI Main Application
Academy Management System
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.auth import admin
from app.auth import student as student_auth
from app.routers import (
    features,
    students,
    classes,
    attendance,
    billing,
    homework,
    notices,
    counseling,
    dashboard
)
from app.config import get_settings

settings = get_settings()

# FastAPI app
app = FastAPI(
    title="Academy Management System",
    description="멀티테넌트 SaaS 학원 관리 시스템",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create uploads directory if it doesn't exist
import os
uploads_dir = os.path.join("static", "uploads", "homework")
os.makedirs(uploads_dir, exist_ok=True)

# Mount uploads directory separately for homework submissions
app.mount("/uploads", StaticFiles(directory="static/uploads"), name="uploads")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(admin.router)
app.include_router(student_auth.router)
app.include_router(features.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(classes.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(homework.router, prefix="/api")
app.include_router(notices.router, prefix="/api")
app.include_router(counseling.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


# ============================================
# Home & Landing Pages
# ============================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.app_name}


# ============================================
# Admin Pages
# ============================================

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@app.get("/admin/features", response_class=HTMLResponse)
async def admin_features(request: Request):
    """Admin feature library page"""
    return templates.TemplateResponse("admin/features.html", {"request": request})


@app.get("/admin/students", response_class=HTMLResponse)
async def admin_students_page(request: Request):
    """Admin students management page"""
    return templates.TemplateResponse("admin/students.html", {"request": request})


@app.get("/admin/attendance", response_class=HTMLResponse)
async def admin_attendance_page(request: Request):
    """Admin attendance page"""
    return templates.TemplateResponse("admin/attendance.html", {"request": request})


@app.get("/admin/billing", response_class=HTMLResponse)
async def admin_billing_page(request: Request):
    """Admin billing page"""
    return templates.TemplateResponse("admin/billing.html", {"request": request})


@app.get("/admin/homework", response_class=HTMLResponse)
async def admin_homework_page(request: Request):
    """Admin homework page"""
    return templates.TemplateResponse("admin/homework.html", {"request": request})


@app.get("/admin/notices", response_class=HTMLResponse)
async def admin_notices_page(request: Request):
    """Admin notices page"""
    return templates.TemplateResponse("admin/notices.html", {"request": request})


@app.get("/admin/counseling", response_class=HTMLResponse)
async def admin_counseling_page(request: Request):
    """Admin counseling page"""
    return templates.TemplateResponse("admin/counseling.html", {"request": request})


# ============================================
# Student Pages
# ============================================

@app.get("/student/login", response_class=HTMLResponse)
async def student_login_page(request: Request):
    """Student login page"""
    return templates.TemplateResponse("student/login.html", {"request": request})


@app.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request):
    """Student dashboard page"""
    return templates.TemplateResponse("student/dashboard.html", {"request": request})


@app.get("/student/portal", response_class=HTMLResponse)
async def student_portal(request: Request):
    """Student portal home (module-based)"""
    return templates.TemplateResponse("student/portal.html", {"request": request})


@app.get("/student/notifications", response_class=HTMLResponse)
async def student_notifications(request: Request):
    """Student notifications page"""
    return templates.TemplateResponse("student/notifications.html", {"request": request})


@app.get("/student/profile", response_class=HTMLResponse)
async def student_profile(request: Request):
    """Student profile page"""
    return templates.TemplateResponse("student/profile.html", {"request": request})


@app.get("/student/attendance", response_class=HTMLResponse)
async def student_attendance_page(request: Request):
    """Student attendance page"""
    return templates.TemplateResponse("student/attendance.html", {"request": request})


@app.get("/student/homework", response_class=HTMLResponse)
async def student_homework_page(request: Request):
    """Student homework page"""
    return templates.TemplateResponse("student/homework.html", {"request": request})


@app.get("/student/notices", response_class=HTMLResponse)
async def student_notices_page(request: Request):
    """Student notices page"""
    return templates.TemplateResponse("student/notices.html", {"request": request})


@app.get("/student/billing", response_class=HTMLResponse)
async def student_billing_page(request: Request):
    """Student billing page"""
    return templates.TemplateResponse("student/billing.html", {"request": request})


@app.get("/student/signup", response_class=HTMLResponse)
async def student_signup_page(request: Request):
    """Student signup page (via invite link)"""
    return templates.TemplateResponse("student/signup.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

