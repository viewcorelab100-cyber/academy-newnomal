from sqlalchemy import Column, Integer, String, DateTime, Time, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Class(Base):
    """반 모델"""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 반 이름
    subject = Column(String)  # 과목
    teacher = Column(String)  # 담당 강사
    schedule = Column(String)  # 수업 일정 (예: 월수금 19:00-21:00)
    monthly_fee = Column(Integer, default=0)  # 월 수강료
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    enrollments = relationship("Enrollment", back_populates="class_")

