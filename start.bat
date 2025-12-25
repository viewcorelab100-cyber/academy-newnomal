@echo off
chcp 65001 >nul
echo ====================================
echo 🏫 학원 관리 시스템 MVP 시작
echo ====================================
echo.

REM 가상환경 활성화
call venv\Scripts\activate

REM 서버 실행
echo 서버를 시작합니다...
echo 브라우저에서 http://localhost:8000 을 열어주세요!
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

