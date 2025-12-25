@echo off
chcp 65001 >nul
echo ====================================
echo 🏫 학원 관리 시스템 MVP 설치
echo ====================================
echo.

REM 가상환경 생성 (없을 경우)
if not exist "venv" (
    echo [1/4] 가상환경 생성 중...
    python -m venv venv
)

REM 가상환경 활성화
echo [2/4] 가상환경 활성화...
call venv\Scripts\activate

REM 라이브러리 설치
echo [3/4] 필요한 라이브러리 설치 중... (1-2분 소요)
pip install -r requirements.txt

REM 데이터베이스 초기화
echo [4/4] 데이터베이스 초기화...
python scripts\init_db.py

echo.
echo ====================================
echo ✅ 설치 완료!
echo ====================================
echo.
echo 이제 start.bat 파일을 더블클릭하면 서버가 실행됩니다!
echo 또는 터미널에서: uvicorn app.main:app --reload
echo.
pause

