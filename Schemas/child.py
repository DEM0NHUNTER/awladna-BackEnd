from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class ChildCreate(BaseModel):
    name: str
    birth_date: datetime
    gender: str
    behavioral_patterns: Optional[Dict] = {}
    emotional_state: Optional[Dict] = {}


class ChildOut(BaseModel):
    child_id: int
    name: str
    birth_date: datetime
    gender: str
    age: int
    behavioral_patterns: Optional[Dict] = {}
    emotional_state: Optional[Dict] = {}
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
