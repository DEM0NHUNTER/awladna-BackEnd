from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional

from BackEnd.Utils.database import Base
from BackEnd.Utils.encryption import encrypt_data, decrypt_data


class ChatLog(Base):
    __tablename__ = "chat_logs"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    child_id = Column(Integer, ForeignKey("child_profiles.child_id"), nullable=False)

    # Encrypted fields
    _user_input = Column("user_input", Text, nullable=False)
    _chatbot_response = Column("chatbot_response", Text, nullable=False)

    # Feedback & metadata
    context = Column(Text)  # Tags or topic
    sentiment_score = Column(Float)  # -1.0 (neg) to 1.0 (pos)
    feedback = Column(Text)  # Optional user comments
    rating = Column(Integer)  # Optional 1-5 star rating
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    child_profile = relationship("ChildProfile", back_populates="chat_logs")
    user = relationship("User", back_populates="chat_logs")

    # Indexes
    __table_args__ = (
        Index("ix_user_child_timestamp", "user_id", "child_id", "timestamp"),
        Index("ix_sentiment_score", "sentiment_score"),
    )

    # Transparent decryption accessors
    @property
    def user_input(self) -> str:
        return decrypt_data(self._user_input) if self._user_input else ""

    @user_input.setter
    def user_input(self, value: str):
        self._user_input = encrypt_data(value)

    @property
    def chatbot_response(self) -> str:
        return decrypt_data(self._chatbot_response) if self._chatbot_response else ""

    @chatbot_response.setter
    def chatbot_response(self, value: str):
        self._chatbot_response = encrypt_data(value)

    def get_conversation(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_input": self.user_input,
            "chatbot_response": self.chatbot_response,
            "sentiment": self.sentiment_score,
            "context": self.context,
        }

    @classmethod
    def create_log(
        cls,
        user_id: int,
        child_id: int,
        user_input: str,
        chatbot_response: str,
        context: Optional[str] = None,
        sentiment_score: Optional[float] = None
    ):
        log = cls()
        log.user_id = user_id
        log.child_id = child_id
        log.user_input = user_input
        log.chatbot_response = chatbot_response
        log.context = context
        log.sentiment_score = sentiment_score
        return log


class SentimentMixin:
    """
    Mixin for classifying sentiment into labels.
    """
    SENTIMENT_THRESHOLDS = {
        "positive": 0.3,
        "negative": -0.3,
        "neutral": 0.0
    }

    sentiment_score: float = None

    def get_sentiment_label(self) -> str:
        if self.sentiment_score is None:
            return "unknown"
        if self.sentiment_score >= self.SENTIMENT_THRESHOLDS["positive"]:
            return "positive"
        elif self.sentiment_score <= self.SENTIMENT_THRESHOLDS["negative"]:
            return "negative"
        return "neutral"
