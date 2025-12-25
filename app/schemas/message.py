from pydantic import BaseModel
from typing import Dict, Any, Optional


class KakaoMessageSend(BaseModel):
    student_id: int
    template_id: str
    variables: Dict[str, Any]
    send_policy: Optional[str] = "IMMEDIATE"


class MessageLogResponse(BaseModel):
    id: int
    recipient_phone: str
    template_id: str
    status: str
    sent_at: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True

