from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CounselingNoteCreate(BaseModel):
    student_id: int
    content: str
    tags: Optional[str] = None
    visibility: str = "PRIVATE"


class CounselingNoteResponse(BaseModel):
    id: int
    student_id: int
    content: str
    tags: Optional[str]
    visibility: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

