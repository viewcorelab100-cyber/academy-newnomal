from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.class_model import Class
from app.models.user import User
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/classes", tags=["반"])


@router.get("/", response_model=List[ClassResponse])
async def list_classes(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반 목록 조회"""
    query = db.query(Class)
    if is_active is not None:
        query = query.filter(Class.is_active == is_active)
    
    classes = query.offset(skip).limit(limit).all()
    return classes


@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반 생성"""
    class_obj = Class(**class_data.dict())
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    return class_obj


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반 상세 조회"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="반을 찾을 수 없습니다")
    return class_obj


@router.patch("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반 정보 수정"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="반을 찾을 수 없습니다")
    
    for field, value in class_data.dict(exclude_unset=True).items():
        setattr(class_obj, field, value)
    
    db.commit()
    db.refresh(class_obj)
    return class_obj


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반 삭제 (실제로는 비활성화)"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="반을 찾을 수 없습니다")
    
    class_obj.is_active = False
    db.commit()

