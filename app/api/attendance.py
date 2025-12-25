from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date
from app.database import get_db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.attendance import AttendanceCheck, AttendanceResponse, AttendanceUpdate
from app.services.auth import get_current_user
from app.services.kakao import kakao_service

router = APIRouter(prefix="/attendance", tags=["출석"])


@router.post("/check", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def check_attendance(
    attendance_data: AttendanceCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """출석 체크 (등원/하원)"""
    # 학생 조회
    student = db.query(Student).filter(Student.id == attendance_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    # 오늘 날짜 체크 (하루에 IN/OUT 각 1번만)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    existing_attendance = db.query(Attendance).filter(
        and_(
            Attendance.student_id == attendance_data.student_id,
            Attendance.type == attendance_data.type,
            Attendance.timestamp >= today_start,
            Attendance.timestamp <= today_end
        )
    ).first()
    
    if existing_attendance:
        type_kr = "등원" if attendance_data.type == "in" else "하원"
        raise HTTPException(
            status_code=400, 
            detail=f"이미 오늘 {type_kr} 체크를 완료했습니다"
        )
    
    # 출석 기록 생성
    attendance = Attendance(
        student_id=attendance_data.student_id,
        type=attendance_data.type,
        timestamp=datetime.now()
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    # 학부모에게 카카오톡 알림 발송
    try:
        await kakao_service.send_attendance_notification(
            db=db,
            parent_phone=student.parent_phone,
            student_name=student.name,
            attendance_type=attendance_data.type,
            timestamp=attendance.timestamp.strftime("%Y-%m-%d %H:%M")
        )
    except Exception as e:
        # 알림 실패해도 출석 체크는 완료
        print(f"카카오톡 알림 발송 실패: {e}")
    
    return attendance


@router.get("/", response_model=List[AttendanceResponse])
async def list_attendances(
    date: Optional[str] = Query(None, description="날짜 (YYYY-MM-DD)"),
    class_id: Optional[int] = Query(None, description="반 ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """출석 목록 조회 (날짜, 반 필터링)"""
    query = db.query(Attendance).join(Student)
    
    # 날짜 필터
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            date_start = datetime.combine(target_date, datetime.min.time())
            date_end = datetime.combine(target_date, datetime.max.time())
            query = query.filter(
                and_(
                    Attendance.timestamp >= date_start,
                    Attendance.timestamp <= date_end
                )
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    # 반 필터
    if class_id:
        query = query.join(Enrollment).filter(
            and_(
                Enrollment.class_id == class_id,
                Enrollment.end_date.is_(None)  # 현재 수강 중
            )
        )
    
    attendances = query.order_by(Attendance.timestamp.desc()).all()
    return attendances


@router.get("/student/{student_id}", response_model=List[AttendanceResponse])
async def get_student_attendance(
    student_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """학생 출석 기록 조회"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    attendances = db.query(Attendance)\
        .filter(Attendance.student_id == student_id)\
        .order_by(Attendance.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return attendances


@router.patch("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """출석 기록 수정 (수동 보정)"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="출석 기록을 찾을 수 없습니다")
    
    # 변경된 필드만 업데이트
    for field, value in attendance_data.dict(exclude_unset=True).items():
        setattr(attendance, field, value)
    
    db.commit()
    db.refresh(attendance)
    return attendance

