from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import hashlib
from app.database import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.student import InviteLinkResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/students", tags=["학생 초대"])


@router.post("/{student_id}/invite", response_model=InviteLinkResponse)
async def create_invite_link(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """학생 초대 링크 생성"""
    # 학생 조회
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    # 이미 카카오 연동된 경우
    if student.kakao_user_id:
        raise HTTPException(
            status_code=400, 
            detail="이미 카카오 계정과 연동된 학생입니다"
        )
    
    # 초대 토큰 생성 (32자 랜덤 문자열)
    invite_token = secrets.token_urlsafe(32)
    
    # 토큰 만료 시간 (24시간)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # QR 코드용 고유 ID 생성 (학생 ID 기반 해시)
    qr_code = hashlib.sha256(f"{student_id}-{invite_token}".encode()).hexdigest()[:16]
    
    # 학생 정보 업데이트
    student.invite_token = invite_token
    student.invite_expires_at = expires_at
    student.qr_code = qr_code
    
    db.commit()
    db.refresh(student)
    
    # 초대 링크 생성
    base_url = "http://localhost:8000"  # 프로덕션에서는 실제 도메인 사용
    invite_url = f"{base_url}/student/signup?token={invite_token}"
    qr_url = f"{base_url}/student/qr/{qr_code}"
    
    return {
        "student_id": student.id,
        "student_name": student.name,
        "invite_url": invite_url,
        "qr_url": qr_url,
        "expires_at": expires_at
    }


@router.get("/{student_id}/invite-status")
async def get_invite_status(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """초대 상태 조회"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
    
    if student.kakao_user_id:
        return {
            "status": "connected",
            "message": "카카오 계정 연동 완료"
        }
    elif student.invite_token and student.invite_expires_at:
        if datetime.utcnow() < student.invite_expires_at:
            return {
                "status": "pending",
                "message": "초대 링크 대기 중",
                "expires_at": student.invite_expires_at
            }
        else:
            return {
                "status": "expired",
                "message": "초대 링크 만료됨"
            }
    else:
        return {
            "status": "none",
            "message": "초대 링크 미생성"
        }

