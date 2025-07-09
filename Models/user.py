# BackEnd/Models/user.py

from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from BackEnd.Utils.database import Base
from BackEnd.Models.settings import UserSettings

# from BackEnd.Models.child_profile import ChildProfile
# from BackEnd.Models.chat_log import ChatLog


class UserRole(str, Enum):
    """Enum for user roles in the application."""
    PARENT = "parent"
    ADMIN = "admin"
    GUEST = "guest"


class User(Base):
    """
    User model representing a parent or admin user in the system.
    Relationships:
      - One-to-many with ChildProfile (a user can have multiple child profiles)
      - One-to-many with ChatLog (a user can have multiple chat logs)
    """
    __tablename__ = "users"

    # Primary key
    user_id = Column(Integer, primary_key=True, index=True)

    # User credentials and info
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.PARENT, nullable=False)
    created_at = Column(DateTime, default=text("now()"))
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    # Relationships
    children = relationship("ChildProfile", back_populates="user", cascade="all, delete-orphan")
    chat_logs = relationship("ChatLog", back_populates="user", cascade="all, delete-orphan")

    # Account status
    is_verified = Column(Boolean, default=True)
    verification_token = Column(String, nullable=True)

    def __repr__(self):
        return f"<User(email={self.email}, role={self.role}, created_at={self.created_at})>"
