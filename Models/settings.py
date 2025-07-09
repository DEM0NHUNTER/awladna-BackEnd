# BackEnd/Models/settings.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from BackEnd.Utils.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    language = Column(String(10), default="en")
    theme = Column(JSON, default='{"primary": "#3b82f6", "secondary": "#8b5cf6", "version": 1}')
    theme_history = Column(JSON, default="[]")

    user = relationship("User", back_populates="settings")