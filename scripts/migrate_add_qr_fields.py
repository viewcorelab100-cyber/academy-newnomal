"""
학생 테이블에 QR 코드 자동 출석 필드 추가
실행: python scripts/migrate_add_qr_fields.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.database import engine


def migrate():
    """마이그레이션 실행"""
    print("🔄 데이터베이스 마이그레이션 시작...")
    
    with engine.connect() as conn:
        # SQLite인지 PostgreSQL인지 확인
        db_url = str(engine.url)
        
        try:
            # 1. kakao_user_id 추가
            print("  - kakao_user_id 컬럼 추가 중...")
            conn.execute(text("""
                ALTER TABLE students 
                ADD COLUMN kakao_user_id VARCHAR UNIQUE
            """))
            print("    ✓ kakao_user_id 추가 완료")
        except Exception as e:
            print(f"    ⚠ kakao_user_id 이미 존재하거나 오류: {e}")
        
        try:
            # 2. invite_token 추가
            print("  - invite_token 컬럼 추가 중...")
            conn.execute(text("""
                ALTER TABLE students 
                ADD COLUMN invite_token VARCHAR UNIQUE
            """))
            print("    ✓ invite_token 추가 완료")
        except Exception as e:
            print(f"    ⚠ invite_token 이미 존재하거나 오류: {e}")
        
        try:
            # 3. invite_expires_at 추가
            print("  - invite_expires_at 컬럼 추가 중...")
            if 'sqlite' in db_url:
                conn.execute(text("""
                    ALTER TABLE students 
                    ADD COLUMN invite_expires_at DATETIME
                """))
            else:
                conn.execute(text("""
                    ALTER TABLE students 
                    ADD COLUMN invite_expires_at TIMESTAMP WITH TIME ZONE
                """))
            print("    ✓ invite_expires_at 추가 완료")
        except Exception as e:
            print(f"    ⚠ invite_expires_at 이미 존재하거나 오류: {e}")
        
        try:
            # 4. qr_code 추가
            print("  - qr_code 컬럼 추가 중...")
            conn.execute(text("""
                ALTER TABLE students 
                ADD COLUMN qr_code VARCHAR UNIQUE
            """))
            print("    ✓ qr_code 추가 완료")
        except Exception as e:
            print(f"    ⚠ qr_code 이미 존재하거나 오류: {e}")
        
        conn.commit()
    
    print("\n✅ 마이그레이션 완료!")
    print("\n📋 추가된 컬럼:")
    print("  - kakao_user_id: 카카오 계정 ID")
    print("  - invite_token: 초대 토큰")
    print("  - invite_expires_at: 초대 만료 시간")
    print("  - qr_code: QR 코드용 고유 ID")


if __name__ == "__main__":
    migrate()

