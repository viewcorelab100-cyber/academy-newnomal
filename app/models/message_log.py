from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base


class MessageLog(Base):
    """메시지 발송 로그 모델"""
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_phone = Column(String, nullable=False)
    template_id = Column(String, nullable=False)  # 카카오톡 템플릿 ID
    send_policy = Column(String)  # 발송 정책 (예: 즉시, 예약)
    payload = Column(Text)  # JSON 형태의 메시지 데이터
    status = Column(String, default="PENDING")  # PENDING, SENT, FAILED
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

