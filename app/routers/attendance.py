"""
출석 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.utils import get_current_user
from app.database import get_supabase_admin
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

router = APIRouter(prefix="/attendance", tags=["attendance"])

class AttendanceCreate(BaseModel):
    student_id: str
    status: str  # present, late, absent, excused
    notes: Optional[str] = None

@router.get("/")
async def list_attendance(
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """출석 기록 조회"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    query = supabase.table("attendance")\
        .select("*, students(name, student_number)")\
        .eq("academy_id", academy_id)
    
    if date:
        query = query.eq("date", date)
    else:
        # 오늘 날짜
        today = datetime.now().date().isoformat()
        query = query.eq("date", today)
    
    response = query.order("created_at", desc=True).execute()
    
    return response.data

@router.post("/")
async def create_attendance(
    attendance: AttendanceCreate,
    current_user: dict = Depends(get_current_user)
):
    """출석 기록 생성"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    data = {
        "academy_id": academy_id,
        "student_id": attendance.student_id,
        "date": datetime.now().date().isoformat(),
        "status": attendance.status,
        "notes": attendance.notes,
        "marked_by": current_user["sub"]
    }
    
    response = supabase.table("attendance").insert(data).execute()
    
    return response.data[0]

@router.get("/stats")
async def attendance_stats(current_user: dict = Depends(get_current_user)):
    """출석 통계"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    today = datetime.now().date().isoformat()
    
    # 오늘 출석 현황
    response = supabase.table("attendance")\
        .select("status")\
        .eq("academy_id", academy_id)\
        .eq("date", today)\
        .execute()
    
    total = len(response.data)
    present = len([r for r in response.data if r["status"] == "present"])
    late = len([r for r in response.data if r["status"] == "late"])
    absent = len([r for r in response.data if r["status"] == "absent"])
    
    return {
        "date": today,
        "total": total,
        "present": present,
        "late": late,
        "absent": absent,
        "attendance_rate": round((present + late) / total * 100, 1) if total > 0 else 0
    }

