"""
공지사항 API
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.utils import get_current_user
from app.database import get_supabase_admin
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/notices", tags=["notices"])

class NoticeCreate(BaseModel):
    title: str
    content: str
    is_important: bool = False
    target_classes: Optional[list] = None

@router.get("/")
async def list_notices(current_user: dict = Depends(get_current_user)):
    """공지사항 목록 조회"""
    supabase = get_supabase_admin()
    
    if current_user["role"] == "admin":
        academy_id = current_user.get("academy_id")
        response = supabase.table("notices")\
            .select("*")\
            .eq("academy_id", academy_id)\
            .order("created_at", desc=True)\
            .execute()
    else:
        # 학생은 자신의 학원 공지만 볼 수 있음
        student_id = current_user["sub"]
        student_response = supabase.table("students")\
            .select("academy_id")\
            .eq("id", student_id)\
            .execute()
        
        if not student_response.data:
            raise HTTPException(status_code=404, detail="학생 정보를 찾을 수 없습니다.")
        
        academy_id = student_response.data[0]["academy_id"]
        response = supabase.table("notices")\
            .select("*")\
            .eq("academy_id", academy_id)\
            .order("created_at", desc=True)\
            .execute()
    
    return response.data

@router.post("/")
async def create_notice(
    notice: NoticeCreate,
    current_user: dict = Depends(get_current_user)
):
    """공지사항 생성"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    data = {
        "academy_id": academy_id,
        "title": notice.title,
        "content": notice.content,
        "is_important": notice.is_important,
        "target_classes": notice.target_classes,
        "created_by": current_user["sub"]
    }
    
    response = supabase.table("notices").insert(data).execute()
    
    return response.data[0]

@router.delete("/{notice_id}")
async def delete_notice(notice_id: str, current_user: dict = Depends(get_current_user)):
    """공지사항 삭제"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    
    response = supabase.table("notices")\
        .delete()\
        .eq("id", notice_id)\
        .execute()
    
    return {"message": "공지사항이 삭제되었습니다."}

