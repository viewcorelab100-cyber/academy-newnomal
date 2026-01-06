"""
Student Authentication (Kakao OAuth)
"""
from fastapi import APIRouter, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
import httpx
import secrets
from datetime import datetime, timedelta
from app.database import supabase_admin
from app.config import get_settings
from app.auth.utils import create_access_token

settings = get_settings()
router = APIRouter(prefix="/auth/student", tags=["Student Auth"])

# In-memory store for OAuth state (production: use Redis)
oauth_states = {}


@router.get("/invite/verify")
async def verify_invite_token(token: str = Query(...)):
    """Step 1: Verify invite token before OAuth"""
    
    # Query student_invites table
    response = supabase_admin.table("student_invites")\
        .select("*, students!inner(id, name, academy_id, status)")\
        .eq("token", token)\
        .execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효하지 않은 초대 링크입니다"
        )
    
    invite = response.data[0]
    
    # Check if expired
    expires_at = datetime.fromisoformat(invite["expires_at"].replace('Z', '+00:00'))
    if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="만료된 초대 링크입니다. 관리자에게 새 링크를 요청하세요."
        )
    
    # Check if already used
    if invite.get("used_at"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용된 초대 링크입니다"
        )
    
    return {
        "valid": True,
        "student_name": invite["students"]["name"],
        "expires_at": invite["expires_at"]
    }


@router.get("/kakao/login")
async def kakao_login(token: str = Query(...)):
    """Step 2: Redirect to Kakao OAuth with state containing invite token"""
    
    # Verify token first
    await verify_invite_token(token)
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "invite_token": token,
        "created_at": datetime.utcnow()
    }
    
    # Build Kakao OAuth URL
    kakao_auth_url = "https://kauth.kakao.com/oauth/authorize"
    redirect_uri = f"{settings.frontend_url or 'http://localhost:8000'}/auth/student/kakao/callback"
    
    params = {
        "client_id": settings.kakao_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state
    }
    
    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    
    return RedirectResponse(url=f"{kakao_auth_url}?{query_string}")


@router.get("/kakao/callback")
async def kakao_callback(
    code: str = Query(...),
    state: str = Query(...)
):
    """Step 3: Kakao OAuth callback - Exchange code for token, link student account"""
    
    # Verify state
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 state입니다"
        )
    
    invite_token = oauth_states[state]["invite_token"]
    del oauth_states[state]  # Use once
    
    # Exchange code for access token
    token_url = "https://kauth.kakao.com/oauth/token"
    redirect_uri = f"{settings.frontend_url or 'http://localhost:8000'}/auth/student/kakao/callback"
    
    async with httpx.AsyncClient() as client:
        token_data_payload = {
            "grant_type": "authorization_code",
            "client_id": settings.kakao_client_id,
            "redirect_uri": redirect_uri,
            "code": code
        }
        
        # Add client_secret if configured
        if settings.kakao_client_secret:
            token_data_payload["client_secret"] = settings.kakao_client_secret
        
        print(f"🔑 Requesting Kakao Token with:")
        print(f"  - client_id: {settings.kakao_client_id[:10]}...")
        print(f"  - redirect_uri: {redirect_uri}")
        print(f"  - code: {code[:20]}...")
        
        token_response = await client.post(
            token_url,
            data=token_data_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if token_response.status_code != 200:
            error_body = token_response.text
            print(f"❌ Kakao Token Error ({token_response.status_code}): {error_body}")
            try:
                error_json = token_response.json()
                error_msg = error_json.get('error_description', error_json.get('error', '알 수 없는 오류'))
            except:
                error_msg = error_body[:200]
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"카카오 토큰 발급 실패: {error_msg}"
            )
        
        token_data = token_response.json()
        access_token = token_data["access_token"]
        
        # Get user info from Kakao
        user_info_response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_info_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카카오 사용자 정보 조회 실패"
            )
        
        user_info = user_info_response.json()
        kakao_user_id = str(user_info["id"])
        kakao_email = user_info.get("kakao_account", {}).get("email")
        kakao_name = user_info.get("kakao_account", {}).get("profile", {}).get("nickname")
    
    # Step 4: Upsert user_account
    user_account_response = supabase_admin.table("user_accounts")\
        .select("id")\
        .eq("provider", "KAKAO")\
        .eq("provider_user_id", kakao_user_id)\
        .execute()
    
    if user_account_response.data and len(user_account_response.data) > 0:
        user_account_id = user_account_response.data[0]["id"]
    else:
        # Create new user_account
        new_account = supabase_admin.table("user_accounts")\
            .insert({
                "provider": "KAKAO",
                "provider_user_id": kakao_user_id,
                "email": kakao_email,
                "name": kakao_name
            })\
            .execute()
        
        if not new_account.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 계정 생성 실패"
            )
        
        user_account_id = new_account.data[0]["id"]
    
    # Step 5: Get student_id from invite
    invite_response = supabase_admin.table("student_invites")\
        .select("student_id, students!inner(id, name, academy_id)")\
        .eq("token", invite_token)\
        .execute()
    
    if not invite_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="초대 정보를 찾을 수 없습니다"
        )
    
    student_id = invite_response.data[0]["student_id"]
    academy_id = invite_response.data[0]["students"]["academy_id"]
    
    # Step 6: Create student_link
    supabase_admin.table("student_links")\
        .insert({
            "student_id": student_id,
            "user_account_id": user_account_id
        })\
        .execute()
    
    # Step 7: Update student status to ACTIVE
    supabase_admin.table("students")\
        .update({
            "status": "active",
            "is_linked": True,
            "linked_at": datetime.utcnow().isoformat()
        })\
        .eq("id", student_id)\
        .execute()
    
    # Step 8: Mark invite as used
    supabase_admin.table("student_invites")\
        .update({
            "used_at": datetime.utcnow().isoformat(),
            "used_by_user_account_id": user_account_id
        })\
        .eq("token", invite_token)\
        .execute()
    
    # Step 9: Create JWT token for student
    jwt_token = create_access_token(
        data={
            "sub": student_id,
            "academy_id": academy_id,
            "role": "student",
            "user_account_id": user_account_id
        }
    )
    
    # Redirect to student dashboard with token
    redirect_url = f"{settings.frontend_url or 'http://localhost:8000'}/student/dashboard?token={jwt_token}"
    return RedirectResponse(url=redirect_url)


@router.get("/kakao/login-existing")
async def kakao_login_existing():
    """Step 10: Login for existing students (no invite token)"""
    
    # Generate state
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "invite_token": None,  # No invite token for existing users
        "created_at": datetime.utcnow()
    }
    
    # Build Kakao OAuth URL
    kakao_auth_url = "https://kauth.kakao.com/oauth/authorize"
    redirect_uri = f"{settings.frontend_url or 'http://localhost:8000'}/auth/student/kakao/callback-existing"
    
    params = {
        "client_id": settings.kakao_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state
    }
    
    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    
    return RedirectResponse(url=f"{kakao_auth_url}?{query_string}")


@router.get("/kakao/callback-existing")
async def kakao_callback_existing(
    code: str = Query(...),
    state: str = Query(...)
):
    """Step 11: Kakao callback for existing student login"""
    
    # Verify state
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 state입니다"
        )
    
    del oauth_states[state]
    
    # Exchange code for access token
    token_url = "https://kauth.kakao.com/oauth/token"
    redirect_uri = f"{settings.frontend_url or 'http://localhost:8000'}/auth/student/kakao/callback-existing"
    
    async with httpx.AsyncClient() as client:
        token_data_payload_existing = {
            "grant_type": "authorization_code",
            "client_id": settings.kakao_client_id,
            "redirect_uri": redirect_uri,
            "code": code
        }
        
        # Add client_secret if configured
        if settings.kakao_client_secret:
            token_data_payload_existing["client_secret"] = settings.kakao_client_secret
        
        token_response = await client.post(
            token_url,
            data=token_data_payload_existing
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카카오 토큰 발급 실패"
            )
        
        token_data = token_response.json()
        access_token = token_data["access_token"]
        
        # Get user info
        user_info_response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        user_info = user_info_response.json()
        kakao_user_id = str(user_info["id"])
    
    # Find user_account
    user_account_response = supabase_admin.table("user_accounts")\
        .select("id")\
        .eq("provider", "KAKAO")\
        .eq("provider_user_id", kakao_user_id)\
        .execute()
    
    if not user_account_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록되지 않은 계정입니다. 초대 링크를 통해 먼저 가입해주세요."
        )
    
    user_account_id = user_account_response.data[0]["id"]
    
    # Find linked student
    student_link_response = supabase_admin.table("student_links")\
        .select("student_id, students!inner(id, name, academy_id, status)")\
        .eq("user_account_id", user_account_id)\
        .execute()
    
    if not student_link_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="연결된 학생 정보가 없습니다"
        )
    
    student = student_link_response.data[0]["students"]
    
    # Create JWT token
    jwt_token = create_access_token(
        data={
            "sub": student["id"],
            "academy_id": student["academy_id"],
            "role": "student",
            "user_account_id": user_account_id
        }
    )
    
    # Redirect to student dashboard
    redirect_url = f"{settings.frontend_url or 'http://localhost:8000'}/student/dashboard?token={jwt_token}"
    return RedirectResponse(url=redirect_url)
