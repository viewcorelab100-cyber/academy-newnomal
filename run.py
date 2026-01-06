"""
서버 실행 스크립트
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # app/main.py의 app을 실행
        host="0.0.0.0",
        port=8000,
        reload=True
    )

