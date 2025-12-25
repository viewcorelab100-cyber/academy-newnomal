"""
카카오 OAuth 인증 플로우
학생이 초대 링크를 통해 카카오 로그인하는 전체 플로우 처리
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import urlencode
import secrets
from app.database import get_db
from app.models.student import Student
from app.services.kakao import kakao_service
from app.config import settings

router = APIRouter(tags=["카카오 OAuth"])


# 임시 state 저장소 (프로덕션에서는 Redis나 DB 사용 권장)
# key: state_token, value: {"invite_token": str, "created_at": datetime}
STATE_STORE: dict = {}


def cleanup_expired_states():
    """만료된 state 정리 (5분 이상 된 것)"""
    now = datetime.utcnow()
    expired_keys = [
        key for key, value in STATE_STORE.items()
        if (now - value["created_at"]).total_seconds() > 300
    ]
    for key in expired_keys:
        del STATE_STORE[key]


@router.get("/student/signup")
async def student_signup_entry(
    token: str = Query(..., description="초대 토큰"),
    db: Session = Depends(get_db)
):
    """
    1단계: 학생 초대 링크 진입
    초대 토큰을 검증하고 카카오 로그인으로 리다이렉트
    """
    # 초대 토큰으로 학생 조회
    student = db.query(Student).filter(Student.invite_token == token).first()
    
    if not student:
        return HTMLResponse(
            content="""
            <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h2>❌ 유효하지 않은 초대 링크입니다</h2>
                    <p>초대 링크가 올바르지 않습니다. 관리자에게 문의하세요.</p>
                </body>
            </html>
            """,
            status_code=400
        )
    
    # 토큰 만료 확인
    if not student.invite_expires_at or datetime.utcnow() > student.invite_expires_at:
        return HTMLResponse(
            content="""
            <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h2>⏰ 초대 링크가 만료되었습니다</h2>
                    <p>초대 링크의 유효기간이 지났습니다. 관리자에게 새 링크를 요청하세요.</p>
                </body>
            </html>
            """,
            status_code=400
        )
    
    # 이미 카카오 연동된 경우
    if student.kakao_user_id:
        return HTMLResponse(
            content=f"""
            <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h2>✅ 이미 가입 완료된 계정입니다</h2>
                    <p>{student.name}님은 이미 카카오 계정과 연동되어 있습니다.</p>
                    <p><a href="/student/qr/{student.qr_code}">내 QR 코드 보기</a></p>
                </body>
            </html>
            """,
            status_code=200
        )
    
    # CSRF 방지를 위한 state 생성 (초대 토큰 + 랜덤 값)
    state_token = secrets.token_urlsafe(32)
    cleanup_expired_states()
    STATE_STORE[state_token] = {
        "invite_token": token,
        "created_at": datetime.utcnow()
    }
    
    # 카카오 로그인 시작 페이지로 리다이렉트
    return RedirectResponse(
        url=f"/auth/kakao/start?state={state_token}",
        status_code=302
    )


@router.get("/auth/kakao/start")
async def kakao_oauth_start(
    state: str = Query(..., description="State 토큰")
):
    """
    2단계: 카카오 OAuth 인증 시작
    카카오 인증 서버로 리다이렉트
    """
    # State 검증
    if state not in STATE_STORE:
        return HTMLResponse(
            content="""
            <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h2>❌ 잘못된 접근입니다</h2>
                    <p>인증 요청이 유효하지 않습니다. 처음부터 다시 시도해주세요.</p>
                </body>
            </html>
            """,
            status_code=400
        )
    
    # 카카오 인증 URL 생성
    kakao_auth_url = "https://kauth.kakao.com/oauth/authorize"
    params = {
        "client_id": settings.KAKAO_REST_KEY,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "response_type": "code",
        "state": state,
    }
    
    authorize_url = f"{kakao_auth_url}?{urlencode(params)}"
    
    return RedirectResponse(url=authorize_url, status_code=302)


@router.get("/auth/kakao/callback")
async def kakao_oauth_callback(
    code: str = Query(..., description="카카오 인가 코드"),
    state: str = Query(..., description="State 토큰"),
    db: Session = Depends(get_db)
):
    """
    3단계: 카카오 OAuth 콜백 처리
    인가 코드를 받아서 액세스 토큰으로 교환하고 사용자 정보 조회
    """
    try:
        # State 검증
        if state not in STATE_STORE:
            raise HTTPException(
                status_code=400,
                detail="유효하지 않은 state 파라미터입니다"
            )
        
        state_data = STATE_STORE[state]
        invite_token = state_data["invite_token"]
        
        # State 사용 후 삭제 (1회성)
        del STATE_STORE[state]
        
        # 초대 토큰 재검증
        student = db.query(Student).filter(Student.invite_token == invite_token).first()
        
        if not student:
            raise HTTPException(
                status_code=404,
                detail="유효하지 않은 초대 토큰입니다"
            )
        
        # 토큰 만료 재확인
        if not student.invite_expires_at or datetime.utcnow() > student.invite_expires_at:
            raise HTTPException(
                status_code=400,
                detail="초대 링크가 만료되었습니다"
            )
        
        # 이미 연동된 경우
        if student.kakao_user_id:
            raise HTTPException(
                status_code=400,
                detail="이미 카카오 계정과 연동된 학생입니다"
            )
        
        # (A) 인가 코드로 액세스 토큰 받기
        token_data = await kakao_service.get_kakao_access_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=500,
                detail="카카오 액세스 토큰을 받지 못했습니다"
            )
        
        # (B) 액세스 토큰으로 사용자 정보 조회
        user_info = await kakao_service.get_kakao_user_info(access_token)
        kakao_user_id = str(user_info.get("id"))
        
        if not kakao_user_id:
            raise HTTPException(
                status_code=500,
                detail="카카오 사용자 ID를 받지 못했습니다"
            )
        
        # (C) 중복 카카오 계정 확인
        existing_student = db.query(Student).filter(
            Student.kakao_user_id == kakao_user_id
        ).first()
        
        if existing_student:
            raise HTTPException(
                status_code=400,
                detail="이미 다른 학생에게 연동된 카카오 계정입니다"
            )
        
        # (D) 학생 정보에 카카오 계정 연동
        student.kakao_user_id = kakao_user_id
        student.invite_token = None  # 토큰 무효화 (1회성)
        student.invite_expires_at = None
        
        db.commit()
        db.refresh(student)
        
        # 성공 페이지로 리다이렉트
        return RedirectResponse(
            url=f"/student/signup/success?studentId={student.id}",
            status_code=302
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"카카오 OAuth 콜백 오류: {e}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h2>❌ 카카오 로그인 중 오류가 발생했습니다</h2>
                    <p>오류 내용: {str(e)}</p>
                    <p>문제가 계속되면 관리자에게 문의하세요.</p>
                </body>
            </html>
            """,
            status_code=500
        )


@router.get("/student/signup/success")
async def student_signup_success(
    studentId: int = Query(..., description="학생 ID"),
    db: Session = Depends(get_db)
):
    """
    4단계: 가입 완료 페이지
    """
    student = db.query(Student).filter(Student.id == studentId).first()
    
    if not student:
        return HTMLResponse(
            content="""
            <html>
                <head><meta charset="utf-8"></head>
                <body>
                    <h2>❌ 학생 정보를 찾을 수 없습니다</h2>
                </body>
            </html>
            """,
            status_code=404
        )
    
    return HTMLResponse(
        content=f"""
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        text-align: center;
                        background: #f5f5f5;
                    }}
                    .success-box {{
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{ color: #1DB954; margin-bottom: 20px; }}
                    .student-name {{ font-size: 24px; font-weight: bold; margin: 20px 0; }}
                    .qr-link {{
                        display: inline-block;
                        margin-top: 30px;
                        padding: 15px 30px;
                        background: #FEE500;
                        color: #000;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        transition: transform 0.2s;
                    }}
                    .qr-link:hover {{
                        transform: scale(1.05);
                    }}
                </style>
            </head>
            <body>
                <div class="success-box">
                    <h1>✅ 가입 완료!</h1>
                    <div class="student-name">{student.name}님</div>
                    <p>카카오 계정 연동이 완료되었습니다.</p>
                    <p>이제 QR 코드로 출석 체크를 할 수 있습니다.</p>
                    <a href="/student/qr/{student.qr_code}" class="qr-link">
                        📱 내 QR 코드 보기
                    </a>
                </div>
            </body>
        </html>
        """,
        status_code=200
    )

