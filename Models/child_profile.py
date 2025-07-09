# BackEnd/Models/child_profile.py

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import date
from typing import Dict
import json
import logging

from BackEnd.Utils.database import Base
from BackEnd.Utils.encryption import encrypt_data, decrypt_data

logger = logging.getLogger(__name__)


class ChildProfile(Base):
    __tablename__ = "child_profiles"

    child_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=False)  # ✅ Fixed to Date (not DateTime)
    gender = Column(String(10), nullable=False)

    _behavioral_data = Column("behavioral_patterns", Text, nullable=True)
    _emotional_data = Column("emotional_state", Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="children")
    chat_logs = relationship("ChatLog", back_populates="child_profile")
    recommendations = relationship("Recommendation", back_populates="child_profile")

    @property
    def age(self) -> int:
        if not self.birth_date:
            return 0
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def set_behavioral_data(self, data: Dict):
        try:
            self._behavioral_data = encrypt_data(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to encrypt behavioral data for {self.name}: {e}")
            self._behavioral_data = None

    def get_behavioral_data(self, safe: bool = False) -> Dict:
        if not self._behavioral_data:
            return {}
        try:
            return json.loads(decrypt_data(self._behavioral_data))
        except Exception as e:
            if safe:
                logger.warning(f"[safe] Corrupted behavioral data for child_id={self.child_id}: {e}")
                self._behavioral_data = None
                return {}
            raise

    def set_emotional_data(self, data: Dict):
        try:
            self._emotional_data = encrypt_data(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to encrypt emotional data for {self.name}: {e}")
            self._emotional_data = None

    def get_emotional_data(self, safe: bool = False) -> Dict:
        if not self._emotional_data:
            return {}
        try:
            return json.loads(decrypt_data(self._emotional_data))
        except Exception as e:
            if safe:
                logger.warning(f"[safe] Corrupted emotional data for child_id={self.child_id}: {e}")
                self._emotional_data = None
                return {}
            raise

    def __repr__(self):
        return f"<ChildProfile {self.name} (Age: {self.age})>"
