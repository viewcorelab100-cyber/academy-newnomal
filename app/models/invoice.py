from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Invoice(Base):
    """청구서 모델"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    month = Column(String, nullable=False)  # YYYY-MM 형식
    amount = Column(Integer, nullable=False)
    status = Column(String, default="UNPAID")  # UNPAID, PAID
    paid_at = Column(DateTime(timezone=True))
    due_date = Column(Date)  # 납부 기한
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="invoices")

