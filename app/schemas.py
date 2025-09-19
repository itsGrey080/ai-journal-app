from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class EntryCreate(BaseModel):
    content: str = Field(min_length=10, max_length=5000)

class EntryRead(BaseModel):
    id: int
    content: str
    sentiment: str
    keywords: List[str]
    created_at: datetime

    class Config:
        from_attributes = True
