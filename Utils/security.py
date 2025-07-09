# BackEnd/Utils/security.py

from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import JWTError, jwt
import hashlib
from itsdangerous import URLSafeTimedSerializer
from typing import Optional
from BackEnd.Utils.config import settings
# JWT Token Creation
from typing import Union

# Configuration
SECRET_KEY = settings.APP_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Serializer for email verification and password reset tokens
serializer = URLSafeTimedSerializer(SECRET_KEY)


# Password Hashing
def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    # Ensure the data is a dictionary
    to_encode = dict(data) if isinstance(data, dict) else {}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # Adding the expiration directly
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Union[str, dict] = None, expires_delta: timedelta = None) -> str:
    # Ensure data is a dictionary, otherwise default to using the email
    if isinstance(data, str):
        data = {"sub": data}

    elif not isinstance(data, dict):
        data = {}
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    # Adding the expiration directly
    data["exp"] = expire
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# JWT Token Decoding


# Refresh Token Validation
def validate_refresh_token(token: str) -> str:
    payload = decode_token(token)
    return payload.get("sub")


# Email Verification
def generate_verification_token(email: str) -> str:
    return serializer.dumps(email, salt="email-verification")


# Password Reset
def generate_password_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="password-reset")


def verify_email_token(token: str, max_age: int = 3600) -> Optional[str]:
    try:
        return serializer.loads(token, salt="email-verification", max_age=max_age)
    except Exception:
        return None


def verify_password_reset_token(token: str, max_age: int = 3600) -> Optional[str]:
    try:
        return serializer.loads(token, salt="password-reset", max_age=max_age)
    except Exception:
        return None


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTError("Token expired")
    except JWTError:
        raise JWTError("Invalid token")
