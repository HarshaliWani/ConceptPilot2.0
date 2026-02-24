# backend/app/models/flashcard.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FlashcardBase(BaseModel):
    topic: str
    front: str
    back: str
    difficulty: str  # easy, medium, hard
    explanation: Optional[str] = None


class FlashcardCreate(FlashcardBase):
    user_id: str


class Flashcard(FlashcardBase):
    """Flashcard document in MongoDB"""
    id: str = Field(alias="_id")
    user_id: str
    confidence: int = 0  # 0-5 rating
    ease_factor: float = 2.5  # SM-2 algorithm default
    interval: int = 0  # Days until next review
    repetitions: int = 0  # Number of successful reviews
    next_review_date: datetime
    last_reviewed: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True


class FlashcardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    difficulty: Optional[str] = None
    explanation: Optional[str] = None


class FlashcardReview(BaseModel):
    """Update flashcard after review with confidence rating"""
    confidence: int  # 1-5 stars
