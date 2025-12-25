from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class EnrollmentBase(BaseModel):
    student_id: int
    class_id: int
    start_date: date


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentResponse(EnrollmentBase):
    id: int
    end_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True

