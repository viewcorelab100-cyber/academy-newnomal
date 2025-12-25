import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.config import settings
from app.models.message_log import MessageLog


class KakaoService:
    """카카오톡 알림톡/친구톡 발송 서비스"""
    
    KAKAO_API_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    @staticmethod
    async def send_alimtalk(
        db: Session,
        recipient_phone: str,
        template_id: str,
        variables: Dict[str, Any],
        send_policy: str = "IMMEDIATE"
    ) -> MessageLog:
        """
        알림톡 발송
        
        Args:
            db: 데이터베이스 세션
            recipient_phone: 수신자 전화번호
            template_id: 카카오톡 템플릿 ID
            variables: 템플릿 변수
            send_policy: 발송 정책
        """
        # 메시지 로그 생성
        message_log = MessageLog(
            recipient_phone=recipient_phone,
            template_id=template_id,
            send_policy=send_policy,
            payload=json.dumps(variables, ensure_ascii=False),
            status="PENDING"
        )
        db.add(message_log)
        db.commit()
        db.refresh(message_log)
        
        try:
            # 카카오톡 API 호출
            # 실제 환경에서는 카카오톡 비즈니스 API를 사용합니다
            # 여기서는 구조만 제공합니다
            
            headers = {
                "Authorization": f"Bearer {settings.KAKAO_REST_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "template_id": template_id,
                "receiver_uuids": [recipient_phone],
                "variables": variables
            }
            
            # MVP에서는 실제 발송 대신 로그만 기록
            # 실제 프로덕션에서는 아래 주석을 해제하고 사용
            """
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.KAKAO_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    message_log.status = "SENT"
                    message_log.sent_at = datetime.utcnow()
                else:
                    message_log.status = "FAILED"
                    message_log.error_message = response.text
            """
            
            # MVP용 시뮬레이션
            message_log.status = "SENT"
            message_log.sent_at = datetime.utcnow()
            
        except Exception as e:
            message_log.status = "FAILED"
            message_log.error_message = str(e)
        
        db.commit()
        db.refresh(message_log)
        return message_log
    
    @staticmethod
    async def send_attendance_notification(
        db: Session,
        parent_phone: str,
        student_name: str,
        attendance_type: str,
        timestamp: str
    ) -> MessageLog:
        """출석 알림 발송"""
        template_id = (
            settings.KAKAO_ALIMTALK_TEMPLATE_IN 
            if attendance_type == "in" 
            else settings.KAKAO_ALIMTALK_TEMPLATE_OUT
        )
        
        variables = {
            "studentName": student_name,
            "type": "등원" if attendance_type == "in" else "하원",
            "timestamp": timestamp
        }
        
        return await KakaoService.send_alimtalk(
            db, parent_phone, template_id, variables
        )
    
    @staticmethod
    async def send_counseling_notification(
        db: Session,
        parent_phone: str,
        student_name: str,
        counseling_content: str
    ) -> MessageLog:
        """상담 내용 알림 발송"""
        template_id = settings.KAKAO_ALIMTALK_TEMPLATE_COUNSELING
        
        variables = {
            "studentName": student_name,
            "content": counseling_content
        }
        
        return await KakaoService.send_alimtalk(
            db, parent_phone, template_id, variables
        )
    
    @staticmethod
    async def send_billing_notification(
        db: Session,
        parent_phone: str,
        student_name: str,
        month: str,
        amount: int,
        invoice_id: int
    ) -> MessageLog:
        """청구서 알림 발송"""
        template_id = settings.KAKAO_ALIMTALK_TEMPLATE_BILLING
        
        variables = {
            "studentName": student_name,
            "month": month,
            "amount": f"{amount:,}원",
            "invoiceId": str(invoice_id)
        }
        
        return await KakaoService.send_alimtalk(
            db, parent_phone, template_id, variables
        )
    
    @staticmethod
    async def send_overdue_notification(
        db: Session,
        parent_phone: str,
        student_name: str,
        month: str,
        amount: int,
        invoice_id: int
    ) -> MessageLog:
        """미납 알림 발송"""
        template_id = settings.KAKAO_ALIMTALK_TEMPLATE_OVERDUE
        
        variables = {
            "studentName": student_name,
            "month": month,
            "amount": f"{amount:,}원",
            "invoiceId": str(invoice_id)
        }
        
        return await KakaoService.send_alimtalk(
            db, parent_phone, template_id, variables
        )
    
    # ===== OAuth 관련 메서드 =====
    
    @staticmethod
    async def get_kakao_access_token(authorization_code: str) -> Dict[str, Any]:
        """
        카카오 인가 코드로 액세스 토큰 받기
        
        Args:
            authorization_code: 카카오 인가 코드
            
        Returns:
            액세스 토큰 정보 (access_token, refresh_token, expires_in 등)
        """
        token_url = "https://kauth.kakao.com/oauth/token"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": authorization_code,
        }
        
        # Client Secret이 있는 경우 추가
        if settings.KAKAO_CLIENT_SECRET:
            data["client_secret"] = settings.KAKAO_CLIENT_SECRET
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    raise HTTPException(
                        status_code=400,
                        detail=f"카카오 토큰 요청 실패: {error_data.get('error_description', '알 수 없는 오류')}"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"카카오 API 통신 오류: {str(e)}"
            )
    
    @staticmethod
    async def get_kakao_user_info(access_token: str) -> Dict[str, Any]:
        """
        카카오 액세스 토큰으로 사용자 정보 조회
        
        Args:
            access_token: 카카오 액세스 토큰
            
        Returns:
            사용자 정보 (id, kakao_account 등)
        """
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    user_info_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    raise HTTPException(
                        status_code=400,
                        detail=f"카카오 사용자 정보 조회 실패: {error_data.get('msg', '알 수 없는 오류')}"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"카카오 API 통신 오류: {str(e)}"
            )


kakao_service = KakaoService()

