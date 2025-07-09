# BackEnd/Schemas/feedback.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    chat_log_id: str
    rating: int  # 1-5
    comment: str = ""
    timestamp: Optional[datetime] = None