"""
데이터베이스 초기화 스크립트
테이블 생성 및 초기 관리자 계정 생성
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, engine, SessionLocal
from app.models import User, Student, Class, Enrollment, Attendance, Invoice, CounselingNote, MessageLog
from app.services.auth import get_password_hash


def init_database():
    """데이터베이스 초기화"""
    print("데이터베이스 테이블 생성 중...")
    
    # 기존 테이블 모두 삭제
    print("  - 기존 테이블 삭제 중...")
    Base.metadata.drop_all(bind=engine)
    print("  - ✓ 기존 테이블 삭제 완료")
    
    # 새로운 스키마로 테이블 생성
    print("  - 새 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)
    print("✓ 테이블 생성 완료")
    
    # 초기 관리자 계정 생성
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == "admin@academy.com").first()
        if not existing_admin:
            admin = User(
                email="admin@academy.com",
                hashed_password=get_password_hash("admin123"),
                full_name="관리자",
                is_superuser=True
            )
            db.add(admin)
            db.commit()
            print("✓ 초기 관리자 계정 생성 완료")
            print("  이메일: admin@academy.com")
            print("  비밀번호: admin123")
        else:
            print("✓ 관리자 계정이 이미 존재합니다")
    
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n데이터베이스 초기화 완료!")


if __name__ == "__main__":
    init_database()

