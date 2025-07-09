# BackEnd/Utils/auth_utils.py

from typing import Optional, cast

from jose import JWTError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import URLSafeTimedSerializer

from BackEnd.Models.user import User, UserRole
from BackEnd.Utils.database import Session as SessionFactory
from BackEnd.Utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_verification_token,
    verify_email_token,
    decode_token,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_email_token_and_mark_verified(token: str) -> Optional[User]:
    """
    1) Decode & validate the token via verify_email_token().
    2) If valid, load user from DB, set is_verified=True, clear verification_token.
    3) Commit and return the updated User instance, or None on failure.
    """
    email = verify_email_token(token)
    if not email:
        return None

    db: Session = SessionFactory()
    try:
        user: Optional[User] = db.query(User).filter(User.email == email).first()
        if user is None:
            return None
        user.is_verified = True
        user.verification_token = None
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def register_user(email: str, password: str) -> Optional[User]:
    """
    Create a new user (unverified). Returns the User instance or None on conflict.
    """
    db: Session = SessionFactory()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"[ERROR] Email {email!r} already registered!")
            return None

        # Prepare verification token
        verification_token = generate_verification_token(email)

        user = User(
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.PARENT,  # Use enum
            is_verified=False,
            verification_token=verification_token,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"[REGISTERED] {email!r}")
        print(f"[INFO] Verification token: {verification_token}")
        return user

    finally:
        db.close()


def login_user(email: str, password: str) -> tuple[Optional[str], Optional[str]]:
    """
    Verify credentials and produce (access_token, refresh_token).
    Returns (None, None) on failure.
    """
    db: Session = SessionFactory()
    try:
        user = db.query(User).filter(User.email == email).first()
    finally:
        db.close()

    if not user or not verify_password(password, user.password_hash):
        print("[LOGIN FAILED] Invalid credentials.")
        return None, None

    # Must be verified
    if not user.is_verified:
        print("[LOGIN FAILED] Email not verified.")
        return None, None

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token(user.email)
    return access_token, refresh_token


def authenticate_user(email: str) -> User:
    """
    Return a verified user or raise Exception.
    """
    db: Session = SessionFactory()
    try:
        # first() returns Optional[User]
        user = db.query(User).filter(User.email == email).first()
    finally:
        db.close()

    if user is None or not user.is_verified:
        raise Exception("[ERROR] User not verified or does not exist.")

    # At this point, user is non-None and verified.
    return cast(User, user)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db: Session = SessionFactory()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:  # Only check user existence
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()

def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required role: {required_role}"
            )
        return current_user

    return role_checker


def access_protected_resource(token: str) -> None:
    """
    Simply decode the token to show it’s valid.
    """
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        print(f"[ACCESS GRANTED] Valid token for {sub!r}.")
    except Exception as e:
        print(f"[ACCESS DENIED] {e}")
