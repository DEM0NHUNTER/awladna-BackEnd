from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from typing import Union

# ─── Models for user authentication ────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    email: EmailStr
    token: str
    refresh_token: str
    expires_in: int


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None


class GoogleAuthRequest(BaseModel):
    token: str


class UserWithToken(UserResponse):
    access_token: str
    token_type: str


# ─── New models for refresh-token flow ─────────────────────────────────────────

class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


