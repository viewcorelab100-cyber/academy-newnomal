from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.student import Student
from pydantic import BaseModel

router = APIRouter(prefix="/student", tags=["학생 인증"])


class KakaoLoginRequest(BaseModel):
    invite_token: str
    kakao_user_id: str
    kakao_nickname: Optional[str] = None


class StudentLoginResponse(BaseModel):
    student_id: int
    name: str
    qr_code: str
    message: str


@router.post("/signup", response_model=StudentLoginResponse)
async def student_signup(
    data: KakaoLoginRequest,
    db: Session = Depends(get_db)
):
    """학생 가입 (카카오 로그인)"""
    # 초대 토큰으로 학생 조회
    student = db.query(Student).filter(
        Student.invite_token == data.invite_token
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=404, 
            detail="유효하지 않은 초대 링크입니다"
        )
    
    # 토큰 만료 확인
    if not student.invite_expires_at or datetime.utcnow() > student.invite_expires_at:
        raise HTTPException(
            status_code=400,
            detail="초대 링크가 만료되었습니다. 관리자에게 새 링크를 요청하세요"
        )
    
    # 이미 연동된 경우
    if student.kakao_user_id:
        raise HTTPException(
            status_code=400,
            detail="이미 연동된 학생입니다"
        )
    
    # 카카오 계정 연동
    student.kakao_user_id = data.kakao_user_id
    student.invite_token = None  # 토큰 무효화
    student.invite_expires_at = None
    
    db.commit()
    db.refresh(student)
    
    return {
        "student_id": student.id,
        "name": student.name,
        "qr_code": student.qr_code,
        "message": f"{student.name}님, 가입이 완료되었습니다!"
    }


@router.post("/checkin", response_model=dict)
async def qr_checkin(
    qr_code: str = Query(..., description="QR 코드"),
    type: str = Query(..., description="in 또는 out"),
    db: Session = Depends(get_db)
):
    """QR 코드로 자동 출석 체크"""
    from app.models.attendance import Attendance
    from app.services.kakao import kakao_service
    from sqlalchemy import and_
    
    # QR 코드로 학생 조회
    student = db.query(Student).filter(Student.qr_code == qr_code).first()
    
    if not student:
        raise HTTPException(
            status_code=404,
            detail="유효하지 않은 QR 코드입니다"
        )
    
    # 카카오 연동 확인
    if not student.kakao_user_id:
        raise HTTPException(
            status_code=400,
            detail="카카오 계정이 연동되지 않은 학생입니다"
        )
    
    # 오늘 이미 체크했는지 확인
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    existing_attendance = db.query(Attendance).filter(
        and_(
            Attendance.student_id == student.id,
            Attendance.type == type,
            Attendance.timestamp >= today_start,
            Attendance.timestamp <= today_end
        )
    ).first()
    
    if existing_attendance:
        type_kr = "등원" if type == "in" else "하원"
        raise HTTPException(
            status_code=400,
            detail=f"이미 오늘 {type_kr} 체크를 완료했습니다"
        )
    
    # 출석 기록 생성
    attendance = Attendance(
        student_id=student.id,
        type=type,
        timestamp=datetime.now()
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    # 학부모에게 카카오톡 알림
    try:
        await kakao_service.send_attendance_notification(
            db=db,
            parent_phone=student.parent_phone,
            student_name=student.name,
            attendance_type=type,
            timestamp=attendance.timestamp.strftime("%Y-%m-%d %H:%M")
        )
    except Exception as e:
        print(f"카카오톡 알림 발송 실패: {e}")
    
    type_kr = "등원" if type == "in" else "하원"
    return {
        "success": True,
        "student_name": student.name,
        "type": type_kr,
        "timestamp": attendance.timestamp.strftime("%Y-%m-%d %H:%M"),
        "message": f"{student.name}님의 {type_kr}이 체크되었습니다!"
    }


@router.get("/info/{qr_code}")
async def get_student_info(
    qr_code: str,
    db: Session = Depends(get_db)
):
    """QR 코드로 학생 정보 조회"""
    student = db.query(Student).filter(Student.qr_code == qr_code).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="유효하지 않은 QR 코드입니다")
    
    return {
        "student_id": student.id,
        "name": student.name,
        "school": student.school,
        "grade": student.grade,
        "is_connected": bool(student.kakao_user_id)
    }

