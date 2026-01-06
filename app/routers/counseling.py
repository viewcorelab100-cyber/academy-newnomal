"""
상담 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.utils import get_current_user
from app.database import get_supabase_admin
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/counseling", tags=["counseling"])

class CounselingCreate(BaseModel):
    student_id: str
    counseling_date: str
    counselor: str
    notes: str
    follow_up_required: bool = False

@router.get("/")
async def list_counseling(current_user: dict = Depends(get_current_user)):
    """상담 기록 목록 조회"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    response = supabase.table("counseling")\
        .select("*, students(name, student_number)")\
        .eq("academy_id", academy_id)\
        .order("counseling_date", desc=True)\
        .execute()
    
    return response.data

@router.post("/")
async def create_counseling(
    counseling: CounselingCreate,
    current_user: dict = Depends(get_current_user)
):
    """상담 기록 생성"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    data = {
        "academy_id": academy_id,
        "student_id": counseling.student_id,
        "counseling_date": counseling.counseling_date,
        "counselor": counseling.counselor,
        "notes": counseling.notes,
        "follow_up_required": counseling.follow_up_required,
        "created_by": current_user["sub"]
    }
    
    response = supabase.table("counseling").insert(data).execute()
    
    return response.data[0]

@router.get("/{counseling_id}")
async def get_counseling(
    counseling_id: str,
    current_user: dict = Depends(get_current_user)
):
    """상담 기록 상세 조회"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    
    response = supabase.table("counseling")\
        .select("*, students(name, student_number)")\
        .eq("id", counseling_id)\
        .execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="상담 기록을 찾을 수 없습니다.")
    
    return response.data[0]

@router.delete("/{counseling_id}")
async def delete_counseling(
    counseling_id: str,
    current_user: dict = Depends(get_current_user)
):
    """상담 기록 삭제"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    
    response = supabase.table("counseling")\
        .delete()\
        .eq("id", counseling_id)\
        .execute()
    
    return {"message": "상담 기록이 삭제되었습니다."}

