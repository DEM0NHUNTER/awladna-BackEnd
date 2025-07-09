# BackEnd/Schemas/chat.py

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ChatRequest(BaseModel):
    """
    Schema for chat request payload.
    Contains all necessary data to process an AI chat request.
    """
    child_id: int
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """
    Schema for AI chat responses.
    Includes the generated response and metadata.
    """
    response: str
    suggested_actions: List[str] = []
    sentiment: str
    timestamp: datetime

class ConversationHistory(BaseModel):
    """
    Schema for historical chat records.
    Used when retrieving past conversations.
    """
    timestamp: datetime  # When conversation occurred
    chatbot_response: str  # AI's response
    context: Optional[str]  # Conversation context tag
    sentiment: float  # Sentiment score (-1.0 to 1.0)
