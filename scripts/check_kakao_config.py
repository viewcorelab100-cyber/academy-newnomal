"""
카카오 OAuth 설정 확인 스크립트
실행: python scripts/check_kakao_config.py
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.config import settings
    
    print("=" * 60)
    print("🔍 카카오 OAuth 설정 확인")
    print("=" * 60)
    print()
    
    # 필수 환경 변수 체크
    required_vars = {
        "KAKAO_REST_KEY": settings.KAKAO_REST_KEY,
        "KAKAO_REDIRECT_URI": settings.KAKAO_REDIRECT_URI,
        "BASE_URL": settings.BASE_URL,
    }
    
    # 선택 환경 변수
    optional_vars = {
        "KAKAO_CLIENT_SECRET": settings.KAKAO_CLIENT_SECRET,
    }
    
    all_ok = True
    
    print("✅ 필수 환경 변수:")
    print("-" * 60)
    for var_name, var_value in required_vars.items():
        if var_value and var_value != "":
            status = "✅ 설정됨"
            display_value = var_value if len(var_value) < 40 else f"{var_value[:37]}..."
        else:
            status = "❌ 미설정"
            display_value = "(없음)"
            all_ok = False
        
        print(f"{var_name:25} : {status}")
        print(f"{'':25}   값: {display_value}")
        print()
    
    print("⚙️  선택 환경 변수:")
    print("-" * 60)
    for var_name, var_value in optional_vars.items():
        if var_value and var_value != "":
            status = "✅ 설정됨"
            display_value = "********" if "SECRET" in var_name else var_value
        else:
            status = "⚪ 미설정 (선택사항)"
            display_value = "(없음)"
        
        print(f"{var_name:25} : {status}")
        if var_value:
            print(f"{'':25}   값: {display_value}")
        print()
    
    print("=" * 60)
    
    if all_ok:
        print("✅ 모든 필수 환경 변수가 설정되었습니다!")
        print()
        print("다음 단계:")
        print("1. 카카오 개발자 콘솔에서 Redirect URI 등록 확인")
        print("   - URL: https://developers.kakao.com/console")
        print(f"   - Redirect URI: {settings.KAKAO_REDIRECT_URI}")
        print()
        print("2. 서버 실행:")
        print("   uvicorn app.main:app --reload")
        print()
        print("3. 테스트:")
        print("   - 관리자 로그인: http://localhost:8000/login")
        print("   - 학생 초대 링크 생성: POST /students/{id}/invite")
        print()
    else:
        print("❌ 일부 필수 환경 변수가 설정되지 않았습니다!")
        print()
        print("해결 방법:")
        print("1. 프로젝트 루트에 .env 파일 생성")
        print("2. 다음 내용 추가:")
        print()
        print("    KAKAO_REST_KEY=your_kakao_rest_api_key")
        print("    KAKAO_REDIRECT_URI=http://localhost:8000/auth/kakao/callback")
        print("    BASE_URL=http://localhost:8000")
        print()
        print("3. 카카오 개발자 콘솔에서 REST API 키 발급")
        print("   - URL: https://developers.kakao.com/console")
        print()
        print("자세한 가이드: docs/kakao-oauth-setup.md")
        print()
    
    print("=" * 60)
    
    # 추가 정보
    print()
    print("📚 참고 문서:")
    print("  - 설정 가이드: docs/kakao-oauth-setup.md")
    print("  - 플로우 예제: docs/kakao-oauth-example.md")
    print("  - 변경 사항: docs/CHANGELOG-kakao-oauth.md")
    print()
    
    sys.exit(0 if all_ok else 1)
    
except Exception as e:
    print("❌ 오류 발생:", str(e))
    print()
    print("가능한 원인:")
    print("1. .env 파일이 없음")
    print("2. 환경 변수 형식 오류")
    print("3. Python 경로 문제")
    print()
    sys.exit(1)

