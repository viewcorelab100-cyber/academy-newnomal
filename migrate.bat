@echo off
chcp 65001 > nul
echo ============================================
echo QR 코드 자동 출석 필드 추가 마이그레이션
echo ============================================
echo.

REM 가상환경 활성화
call venv\Scripts\activate

REM 마이그레이션 실행
python scripts\migrate_add_qr_fields.py

echo.
echo ============================================
echo 마이그레이션 완료! 서버를 재시작해주세요.
echo ============================================
pause

