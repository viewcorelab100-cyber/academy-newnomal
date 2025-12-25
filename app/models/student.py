from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    """학생 모델"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)  # 학생 연락처
    parent_phone = Column(String, nullable=False)  # 학부모 연락처 (카카오톡 발송용)
    school = Column(String)  # 학교명
    grade = Column(String)  # 학년
    notes = Column(Text)  # 메모
    is_active = Column(Boolean, default=True)
    
    # 카카오 연동 필드
    kakao_user_id = Column(String, unique=True, nullable=True)  # 카카오 providerUserId
    invite_token = Column(String, unique=True, nullable=True)  # 초대 토큰
    invite_expires_at = Column(DateTime(timezone=True), nullable=True)  # 초대 만료 시간
    qr_code = Column(String, unique=True, nullable=True)  # QR 코드 (고유 ID)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    enrollments = relationship("Enrollment", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    invoices = relationship("Invoice", back_populates="student")
    counseling_notes = relationship("CounselingNote", back_populates="student")

