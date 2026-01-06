"""
Student Management API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import uuid4
from datetime import datetime, timedelta
import secrets
from app.models.schemas import (
    StudentCreate, StudentUpdate, StudentResponse, StudentInviteResponse, TokenData
)
from app.auth.utils import require_admin, get_current_user
from app.database import supabase_admin
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/me")
async def get_my_profile(
    current_user: TokenData = Depends(get_current_user)
):
    """Get current student's profile (for students)"""
    from datetime import datetime, timedelta
    
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="학생만 접근할 수 있습니다"
        )
    
    # Get student info
    student_response = supabase_admin.table("students")\
        .select("id, name, student_number, phone, email, grade, status, created_at")\
        .eq("id", current_user.user_id)\
        .eq("academy_id", current_user.academy_id)\
        .execute()
    
    if not student_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생 정보를 찾을 수 없습니다"
        )
    
    student = student_response.data[0]
    
    # Get academy info
    academy_response = supabase_admin.table("academies")\
        .select("name")\
        .eq("id", current_user.academy_id)\
        .execute()
    
    academy_name = academy_response.data[0]["name"] if academy_response.data else "알 수 없는 학원"
    
    # Get attendance stats (this month)
    first_day = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    attendance_response = supabase_admin.table("attendance")\
        .select("id", count="exact")\
        .eq("student_id", current_user.user_id)\
        .eq("status", "present")\
        .gte("date", first_day.date().isoformat())\
        .execute()
    
    attendance_count = attendance_response.count or 0
    
    # Get pending homework count
    homework_response = supabase_admin.table("homework_submissions")\
        .select("id", count="exact")\
        .eq("student_id", current_user.user_id)\
        .eq("status", "pending")\
        .execute()
    
    pending_homework = homework_response.count or 0
    
    # Get recent notices
    notices_response = supabase_admin.table("notices")\
        .select("id, title, is_important, created_at")\
        .eq("academy_id", current_user.academy_id)\
        .order("created_at", desc=True)\
        .limit(5)\
        .execute()
    
    recent_notices = []
    for notice in (notices_response.data or []):
        created_at = datetime.fromisoformat(notice["created_at"].replace('Z', '+00:00'))
        days_ago = (datetime.utcnow().replace(tzinfo=created_at.tzinfo) - created_at).days
        date_str = f"{days_ago}일 전" if days_ago > 0 else "오늘"
        
        recent_notices.append({
            "id": notice["id"],
            "title": notice["title"],
            "is_important": notice.get("is_important", False),
            "date": date_str
        })
    
    return {
        "name": student["name"],
        "academy_name": academy_name,
        "student_number": student.get("student_number"),
        "grade": student.get("grade"),
        "stats": {
            "attendance": attendance_count,
            "pendingHomework": pending_homework
        },
        "recent_notices": recent_notices
    }


@router.post("/", response_model=StudentResponse)
async def create_student(
    student: StudentCreate,
    current_user: TokenData = Depends(require_admin)
):
    """Create a new student and generate invite link"""
    
    # Generate invite token
    invite_token = secrets.token_urlsafe(32)
    invite_expires_at = datetime.utcnow() + timedelta(days=7)
    
    # Create student record
    student_data = student.dict(exclude_unset=True)
    student_data.update({
        "academy_id": str(current_user.academy_id),
        "invite_token": invite_token,
        "invite_expires_at": invite_expires_at.isoformat(),
        "is_linked": False,
        "status": "active"
    })
    
    response = supabase_admin.table("students")\
        .insert(student_data)\
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="학생 생성에 실패했습니다"
        )
    
    return response.data[0]


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    status: str = None,
    current_user: TokenData = Depends(require_admin)
):
    """List all students in academy"""
    
    query = supabase_admin.table("students")\
        .select("*")\
        .eq("academy_id", current_user.academy_id)
    
    if status:
        query = query.eq("status", status)
    
    response = query.order("created_at", desc=True).execute()
    
    return response.data


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    current_user: TokenData = Depends(require_admin)
):
    """Get student details"""
    
    response = supabase_admin.table("students")\
        .select("*")\
        .eq("id", student_id)\
        .eq("academy_id", current_user.academy_id)\
        .execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생을 찾을 수 없습니다"
        )
    
    return response.data[0]


@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    current_user: TokenData = Depends(require_admin)
):
    """Update student information"""
    
    # Verify student belongs to academy
    check_response = supabase_admin.table("students")\
        .select("id")\
        .eq("id", student_id)\
        .eq("academy_id", current_user.academy_id)\
        .execute()
    
    if not check_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생을 찾을 수 없습니다"
        )
    
    # Update student
    update_data = student_update.dict(exclude_unset=True)
    response = supabase_admin.table("students")\
        .update(update_data)\
        .eq("id", student_id)\
        .execute()
    
    return response.data[0]


@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    current_user: TokenData = Depends(require_admin)
):
    """Delete student (soft delete by setting status to inactive)"""
    
    response = supabase_admin.table("students")\
        .update({"status": "inactive"})\
        .eq("id", student_id)\
        .eq("academy_id", current_user.academy_id)\
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생을 찾을 수 없습니다"
        )
    
    return {"message": "학생이 비활성화되었습니다"}


@router.post("/{student_id}/invite", response_model=StudentInviteResponse)
async def generate_student_invite(
    student_id: str,
    current_user: TokenData = Depends(require_admin)
):
    """Generate invite link and QR code for student (NEW STRUCTURE)"""
    
    # Get student info
    student_response = supabase_admin.table("students")\
        .select("id, name, academy_id")\
        .eq("id", student_id)\
        .eq("academy_id", current_user.academy_id)\
        .execute()
    
    if not student_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생을 찾을 수 없습니다"
        )
    
    student = student_response.data[0]
    
    # Delete existing invite for this student (if any)
    supabase_admin.table("student_invites")\
        .delete()\
        .eq("student_id", student_id)\
        .execute()
    
    # Generate new invite token
    invite_token = secrets.token_urlsafe(32)
    invite_expires_at = datetime.utcnow() + timedelta(days=7)
    
    # Insert into student_invites table
    invite_response = supabase_admin.table("student_invites")\
        .insert({
            "student_id": student_id,
            "token": invite_token,
            "expires_at": invite_expires_at.isoformat()
        })\
        .execute()
    
    if not invite_response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="초대 생성에 실패했습니다"
        )
    
    # Generate invite link
    base_url = settings.frontend_url or "http://localhost:8000"
    invite_link = f"{base_url}/student/signup?token={invite_token}"
    
    # QR code data (can be used with qrcode library on frontend)
    qr_data = invite_link
    
    return StudentInviteResponse(
        invite_link=invite_link,
        qr_code_data=qr_data,
        expires_at=invite_expires_at,
        student_name=student["name"]
    )


@router.post("/{student_id}/regenerate-invite")
async def regenerate_invite(
    student_id: str,
    current_user: TokenData = Depends(require_admin)
):
    """Regenerate invite token for student (LEGACY - for backwards compatibility)"""
    
    # Use new structure
    return await generate_student_invite(student_id, current_user)

