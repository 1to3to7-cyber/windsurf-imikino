from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    display_name: str = Field(..., min_length=2, max_length=50, description="Display name")
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s_-]+$', v):
            raise ValueError('Display name can only contain letters, numbers, spaces, hyphens and underscores')
        return v.strip()

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")

class TokenData(BaseModel):
    sub: str = Field(..., description="Subject (user email)")
    exp: int = Field(..., description="Expiration timestamp")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class PasswordReset(BaseModel):
    email: EmailStr = Field(..., description="User email address")

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Reset token")
    password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
