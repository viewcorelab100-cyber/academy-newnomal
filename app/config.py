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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

