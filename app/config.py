from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./academy.db"  # SQLite로 임시 변경
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Kakao API
    KAKAO_REST_API_KEY: str = ""
    KAKAO_SENDER_KEY: str = ""
    KAKAO_ALIMTALK_TEMPLATE_IN: str = ""
    KAKAO_ALIMTALK_TEMPLATE_OUT: str = ""
    KAKAO_ALIMTALK_TEMPLATE_COUNSELING: str = ""
    KAKAO_ALIMTALK_TEMPLATE_BILLING: str = ""
    KAKAO_ALIMTALK_TEMPLATE_OVERDUE: str = ""
    
    # Kakao OAuth
    KAKAO_REST_KEY: str = ""  # 카카오 REST API 키 (Client ID)
    KAKAO_CLIENT_SECRET: Optional[str] = None  # 카카오 Client Secret (선택사항)
    KAKAO_REDIRECT_URI: str = "http://localhost:8000/auth/kakao/callback"  # 카카오 Redirect URI
    
    # App Settings
    BASE_URL: str = "http://localhost:8000"  # 애플리케이션 기본 URL
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

