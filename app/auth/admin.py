"""
관리자 인증
"""
from fastapi import APIRouter, Depends, Form, HTTPException
from app.auth.utils import create_access_token, verify_password
from app.database import get_supabase_admin
from datetime import timedelta

router = APIRouter(prefix="/auth/admin", tags=["auth"])

@router.post("/login")
async def admin_login(email: str = Form(...), password: str = Form(...)):
    """관리자 로그인"""
    supabase = get_supabase_admin()
    
    # 사용자 조회
    response = supabase.table("users")\
        .select("*")\
        .eq("email", email)\
        .eq("role", "admin")\
        .execute()
    
    if not response.data:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    
    user = response.data[0]
    
    # 비밀번호 확인
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    
    # JWT 토큰 생성
    access_token = create_access_token(
        data={"sub": user["id"], "role": "admin", "academy_id": user["academy_id"]},
        expires_delta=timedelta(days=7)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

