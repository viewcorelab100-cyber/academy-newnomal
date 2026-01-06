"""
기능 라이브러리 API
"""
from fastapi import APIRouter, Depends
from app.auth.utils import get_current_user

router = APIRouter(prefix="/features", tags=["features"])

@router.get("/")
async def list_features(current_user: dict = Depends(get_current_user)):
    """기능 목록 조회"""
    features = [
        {"id": "1", "name": "학생 관리", "description": "학생 정보 관리", "enabled": True},
        {"id": "2", "name": "출석 관리", "description": "QR코드 출석 체크", "enabled": True},
        {"id": "3", "name": "숙제 관리", "description": "숙제 배정 및 채점", "enabled": True},
        {"id": "4", "name": "결제 관리", "description": "학원비 관리", "enabled": True},
        {"id": "5", "name": "공지사항", "description": "학원 공지사항", "enabled": True},
        {"id": "6", "name": "상담 관리", "description": "학부모 상담 관리", "enabled": True},
    ]
    return features

