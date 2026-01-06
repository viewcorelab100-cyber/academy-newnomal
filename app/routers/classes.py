"""
반 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.utils import get_current_user
from app.database import get_supabase_admin
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/classes", tags=["classes"])

class ClassCreate(BaseModel):
    name: str
    description: Optional[str] = None
    grade_level: Optional[str] = None
    subject: Optional[str] = None

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    grade_level: Optional[str] = None
    subject: Optional[str] = None

@router.get("/")
async def list_classes(current_user: dict = Depends(get_current_user)):
    """반 목록 조회"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    response = supabase.table("classes")\
        .select("*, class_students(count)")\
        .eq("academy_id", academy_id)\
        .order("created_at", desc=True)\
        .execute()
    
    return response.data

@router.post("/")
async def create_class(
    class_data: ClassCreate,
    current_user: dict = Depends(get_current_user)
):
    """반 생성"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    new_class = {
        "academy_id": academy_id,
        "name": class_data.name,
        "description": class_data.description,
        "grade_level": class_data.grade_level,
        "subject": class_data.subject
    }
    
    response = supabase.table("classes").insert(new_class).execute()
    
    return response.data[0]

@router.get("/{class_id}")
async def get_class(class_id: str, current_user: dict = Depends(get_current_user)):
    """반 상세 조회"""
    supabase = get_supabase_admin()
    
    response = supabase.table("classes")\
        .select("*, class_students(student_id, students(*))")\
        .eq("id", class_id)\
        .execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="반을 찾을 수 없습니다.")
    
    return response.data[0]

@router.put("/{class_id}")
async def update_class(
    class_id: str,
    class_data: ClassUpdate,
    current_user: dict = Depends(get_current_user)
):
    """반 정보 수정"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    
    update_data = {k: v for k, v in class_data.dict().items() if v is not None}
    
    response = supabase.table("classes")\
        .update(update_data)\
        .eq("id", class_id)\
        .execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="반을 찾을 수 없습니다.")
    
    return response.data[0]

@router.delete("/{class_id}")
async def delete_class(class_id: str, current_user: dict = Depends(get_current_user)):
    """반 삭제"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    
    response = supabase.table("classes")\
        .delete()\
        .eq("id", class_id)\
        .execute()
    
    return {"message": "반이 삭제되었습니다."}

@router.post("/{class_id}/students/{student_id}")
async def add_student_to_class(
    class_id: str,
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    """반에 학생 추가"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    
    data = {
        "class_id": class_id,
        "student_id": student_id
    }
    
    response = supabase.table("class_students").insert(data).execute()
    
    return response.data[0]

@router.delete("/{class_id}/students/{student_id}")
async def remove_student_from_class(
    class_id: str,
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    """반에서 학생 제거"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    
    response = supabase.table("class_students")\
        .delete()\
        .eq("class_id", class_id)\
        .eq("student_id", student_id)\
        .execute()
    
    return {"message": "학생이 반에서 제거되었습니다."}

