from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional


class AttendanceCheck(BaseModel):
    student_id: int
    type: Literal["in", "out"]


class AttendanceUpdate(BaseModel):
    type: Optional[Literal["in", "out"]] = None
    timestamp: Optional[datetime] = None


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    type: str
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True

