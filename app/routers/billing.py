"""
결제 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.utils import get_current_user
from app.database import get_supabase_admin
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/billing", tags=["billing"])

class PaymentCreate(BaseModel):
    student_id: str
    amount: int
    payment_method: str  # card, cash, transfer
    notes: Optional[str] = None

@router.get("/payments")
async def list_payments(current_user: dict = Depends(get_current_user)):
    """결제 내역 조회"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    response = supabase.table("payments")\
        .select("*, students(name, student_number)")\
        .eq("academy_id", academy_id)\
        .order("paid_at", desc=True)\
        .execute()
    
    return response.data

@router.post("/payments")
async def create_payment(
    payment: PaymentCreate,
    current_user: dict = Depends(get_current_user)
):
    """결제 생성"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    data = {
        "academy_id": academy_id,
        "student_id": payment.student_id,
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "status": "completed",
        "paid_at": datetime.now().isoformat(),
        "notes": payment.notes
    }
    
    response = supabase.table("payments").insert(data).execute()
    
    return response.data[0]

@router.get("/stats")
async def billing_stats(current_user: dict = Depends(get_current_user)):
    """결제 통계"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    supabase = get_supabase_admin()
    academy_id = current_user.get("academy_id")
    
    # 이번 달 매출
    current_month = datetime.now().strftime("%Y-%m")
    
    response = supabase.table("payments")\
        .select("amount")\
        .eq("academy_id", academy_id)\
        .eq("status", "completed")\
        .gte("paid_at", f"{current_month}-01")\
        .execute()
    
    monthly_revenue = sum(p["amount"] for p in response.data)
    
    return {
        "monthly_revenue": monthly_revenue,
        "payment_count": len(response.data)
    }

