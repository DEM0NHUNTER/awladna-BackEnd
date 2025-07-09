from sqlalchemy import Column, Integer, String, Text, Date, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from BackEnd.Utils.database import Base


class RecommendationSource(str, PyEnum):
    PEDIATRICIAN = "pediatrician"
    AI_MODEL = "ai_model"
    PARENT_COMMUNITY = "parent_community"
    EDUCATOR = "educator"


class RecommendationPriority(str, PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child_profiles.child_id"))
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(Enum(RecommendationSource), default=RecommendationSource.AI_MODEL)
    priority = Column(Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM)
    effective_date = Column(Date, nullable=False, default=datetime.utcnow)
    expiration_date = Column(Date, nullable=True)
    type = Column(String(50))  # 'behavior' or 'emotional'
    extra_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    child_profile = relationship("ChildProfile", back_populates="recommendations")  # ✅ Bidirectional link