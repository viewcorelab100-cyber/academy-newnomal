from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClassBase(BaseModel):
    name: str
    subject: Optional[str] = None
    teacher: Optional[str] = None
    schedule: Optional[str] = None
    monthly_fee: int = 0


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    teacher: Optional[str] = None
    schedule: Optional[str] = None
    monthly_fee: Optional[int] = None
    is_active: Optional[bool] = None


class ClassResponse(ClassBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

