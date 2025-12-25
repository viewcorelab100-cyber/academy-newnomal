from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from app.database import get_db
from app.models.invoice import Invoice
from app.models.student import Student
from app.models.enrollment import Enrollment
from app.models.class_model import Class
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from app.services.auth import get_current_user
from app.services.kakao import kakao_service

router = APIRouter(prefix="/billing", tags=["청구/결제"])


@router.post("/run/{month}", response_model=dict)
async def run_monthly_billing(
    month: str,  # YYYY-MM 형식
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """월별 자동 청구 생성"""
    # 해당 월의 활성 수강생 조회
    enrollments = db.query(Enrollment).join(Student).join(Class).filter(
        Student.is_active == True,
        Class.is_active == True,
        Enrollment.end_date.is_(None)  # 현재 수강 중
    ).all()
    
    created_invoices = []
    
    for enrollment in enrollments:
        # 이미 청구서가 있는지 확인
        existing = db.query(Invoice).filter(
            Invoice.student_id == enrollment.student_id,
            Invoice.month == month
        ).first()
        
        if existing:
            continue
        
        # 청구서 생성
        invoice = Invoice(
            student_id=enrollment.student_id,
            month=month,
            amount=enrollment.class_.monthly_fee,
            status="UNPAID",
            due_date=date.today() + relativedelta(days=7)  # 7일 후 납부 기한
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        created_invoices.append(invoice.id)
        
        # 학부모에게 청구서 알림 발송
        try:
            await kakao_service.send_billing_notification(
                db=db,
                parent_phone=enrollment.student.parent_phone,
                student_name=enrollment.student.name,
                month=month,
                amount=enrollment.class_.monthly_fee,
                invoice_id=invoice.id
            )
        except Exception as e:
            print(f"청구서 알림 발송 실패: {e}")
    
    return {
        "month": month,
        "created_count": len(created_invoices),
        "invoice_ids": created_invoices
    }


@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    month: str = None,
    status: str = None,
    student_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """청구서 목록 조회"""
    query = db.query(Invoice)
    
    if month:
        query = query.filter(Invoice.month == month)
    if status:
        query = query.filter(Invoice.status == status)
    if student_id:
        query = query.filter(Invoice.student_id == student_id)
    
    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    return invoices


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """청구서 상태 업데이트 (납부 처리)"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="청구서를 찾을 수 없습니다")
    
    # 납부 처리
    if invoice_data.status == "PAID" and invoice.status != "PAID":
        invoice.status = "PAID"
        invoice.paid_at = datetime.utcnow()
    
    # 기타 필드 업데이트
    for field, value in invoice_data.dict(exclude_unset=True).items():
        if field not in ["status"]:  # status는 위에서 처리
            setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/notify-overdue/{month}", response_model=dict)
async def notify_overdue(
    month: str,
    cohort: int = None,  # 특정 그룹만 선택적으로 알림
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """미납자 알림 발송"""
    # 미납 청구서 조회
    query = db.query(Invoice).join(Student).filter(
        Invoice.month == month,
        Invoice.status == "UNPAID"
    )
    
    overdue_invoices = query.all()
    notified_count = 0
    
    for invoice in overdue_invoices:
        try:
            await kakao_service.send_overdue_notification(
                db=db,
                parent_phone=invoice.student.parent_phone,
                student_name=invoice.student.name,
                month=month,
                amount=invoice.amount,
                invoice_id=invoice.id
            )
            notified_count += 1
        except Exception as e:
            print(f"미납 알림 발송 실패 (invoice_id={invoice.id}): {e}")
    
    return {
        "month": month,
        "overdue_count": len(overdue_invoices),
        "notified_count": notified_count
    }

