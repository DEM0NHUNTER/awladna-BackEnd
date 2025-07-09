# BackEnd/Schemas/settings.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class ThemeHistoryEntry(BaseModel):
    timestamp: datetime
    theme: Dict[str, str]
    scope: str
    action: str
    previous_version: Optional[int] = None
    reverted_to: Optional[int] = None

class UserThemeSchema(BaseModel):
    theme: Dict[str, str]  # Includes version and scoped themes
    theme_history: List[ThemeHistoryEntry] = []  # Versioned theme history