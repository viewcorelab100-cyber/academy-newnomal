from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class InvoiceCreate(BaseModel):
    student_id: int
    month: str  # YYYY-MM
    amount: int
    due_date: Optional[date] = None
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: int
    student_id: int
    month: str
    amount: int
    status: str
    paid_at: Optional[datetime]
    due_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

