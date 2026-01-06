"""
Authentication utilities
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


class TokenData(BaseModel):
    """JWT Token payload data"""
    user_id: Optional[UUID] = None
    academy_id: Optional[UUID] = None
    role: str  # "admin", "teacher", "student"
    user_account_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decode and verify JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Extract data from payload
        user_id = payload.get("sub")
        academy_id = payload.get("academy_id")
        role = payload.get("role")
        user_account_id = payload.get("user_account_id")
        
        if role is None:
            raise credentials_exception
        
        token_data = TokenData(
            user_id=user_id,
            academy_id=academy_id,
            role=role,
            user_account_id=user_account_id
        )
        
        return token_data
        
    except JWTError:
        raise credentials_exception


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    return decode_access_token(token)


async def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Dependency to require admin role"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user


async def require_student(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Dependency to require student role"""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="학생 권한이 필요합니다"
        )
    return current_user

