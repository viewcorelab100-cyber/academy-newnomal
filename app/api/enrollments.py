from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.class_model import Class
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/enrollments", tags=["수강"])


@router.get("/", response_model=List[EnrollmentResponse])
async def list_enrollments(
    student_id: int = None,
    class_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """수강 목록 조회"""
    query = db.query(Enrollment)
    
    if student_id:
        query = query.filter(Enrollment.student_id == student_id)
    if class_id:
        query = query.filter(Enrollment.class_id == class_id)
    
    enrollments = query.offset(skip).limit(limit).all()
    return enrollments


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """수강 등록"""
    # 학생 존재 확인
    student = db.query(Student).filter(Student.id == enrollment_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    # 반 존재 확인
    class_obj = db.query(Class).filter(Class.id == enrollment_data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="반을 찾을 수 없습니다")
    
    # 이미 수강 중인지 확인
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment_data.student_id,
        Enrollment.class_id == enrollment_data.class_id,
        Enrollment.end_date.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="이미 수강 중인 반입니다")
    
    enrollment = Enrollment(**enrollment_data.dict())
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def end_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """수강 종료"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="수강 정보를 찾을 수 없습니다")
    
    from datetime import date
    enrollment.end_date = date.today()
    db.commit()

