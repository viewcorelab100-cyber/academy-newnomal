"""
관리자 계정 생성 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import get_supabase_admin
from app.auth.utils import hash_password
import uuid

def create_admin_account():
    """테스트 관리자 계정 생성"""
    supabase = get_supabase_admin()
    
    # 테스트 학원 생성 또는 조회
    academy_response = supabase.table("academies")\
        .select("*")\
        .eq("name", "테스트 학원")\
        .execute()
    
    if academy_response.data:
        academy_id = academy_response.data[0]["id"]
        print(f"✅ 기존 학원 사용: {academy_id}")
    else:
        # 학원 생성
        academy_data = {
            "id": "a0000000-0000-0000-0000-000000000001",
            "name": "테스트 학원",
            "subscription_tier": "premium",
            "subscription_status": "active"
        }
        academy_response = supabase.table("academies").insert(academy_data).execute()
        academy_id = academy_response.data[0]["id"]
        print(f"✅ 새 학원 생성: {academy_id}")
    
    # 관리자 계정 정보
    admin_email = "admin@test.com"
    admin_password = "admin123"  # 원하는 비밀번호로 변경 가능
    admin_name = "관리자"
    
    # 기존 계정 확인
    existing_user = supabase.table("users")\
        .select("*")\
        .eq("email", admin_email)\
        .execute()
    
    if existing_user.data:
        print(f"⚠️  이미 존재하는 계정입니다: {admin_email}")
        print(f"   이메일: {admin_email}")
        print(f"   비밀번호: {admin_password}")
        return
    
    # 비밀번호 해시
    password_hash = hash_password(admin_password)
    
    # 관리자 계정 생성
    user_data = {
        "id": str(uuid.uuid4()),
        "email": admin_email,
        "password_hash": password_hash,
        "name": admin_name,
        "role": "admin",
        "academy_id": academy_id
    }
    
    try:
        result = supabase.table("users").insert(user_data).execute()
        print("\n✅ 관리자 계정 생성 완료!")
        print("=" * 50)
        print(f"📧 이메일: {admin_email}")
        print(f"🔑 비밀번호: {admin_password}")
        print("=" * 50)
        print("\n🌐 로그인 페이지: http://localhost:8000/admin/login")
    except Exception as e:
        print(f"❌ 계정 생성 실패: {str(e)}")

if __name__ == "__main__":
    create_admin_account()

