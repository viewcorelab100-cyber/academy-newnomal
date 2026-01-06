"""
Application configuration
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Academy Management System"
    app_env: str = "development"
    frontend_url: str = "http://localhost:8000"
    
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Kakao OAuth
    kakao_client_id: str
    kakao_client_secret: str = ""
    kakao_redirect_uri: str = "http://localhost:8000/auth/student/kakao/callback"
    
    # Toss Payments (optional)
    toss_client_key: str = ""
    toss_secret_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()

