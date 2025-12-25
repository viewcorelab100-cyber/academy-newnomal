from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    name: str
    phone: Optional[str] = None
    parent_phone: str
    school: Optional[str] = None
    grade: Optional[str] = None
    notes: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    school: Optional[str] = None
    grade: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    id: int
    is_active: bool
    kakao_user_id: Optional[str]
    qr_code: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class InviteLinkResponse(BaseModel):
    student_id: int
    student_name: str
    invite_url: str
    qr_url: str
    expires_at: datetime

