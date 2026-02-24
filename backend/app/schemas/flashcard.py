# backend/app/schemas/flashcard.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FlashcardGenerateRequestSchema(BaseModel):
    """Request to generate flashcards"""

    topic: str = Field(..., min_length=3, max_length=500)
    is_custom_topic: bool = (
        False  # True if user typed custom topic, False if from syllabus
    )


class FlashcardCreateSchema(BaseModel):
    """Schema for creating a single flashcard"""

    topic: str
    front: str
    back: str
    difficulty: str  # easy, medium, hard
    explanation: Optional[str] = None


class FlashcardResponseSchema(BaseModel):
    """Response schema for flashcard"""

    id: str = Field(alias="_id")
    user_id: str
    topic: str
    front: str
    back: str
    difficulty: str
    explanation: Optional[str] = None
    confidence: int
    ease_factor: float
    interval: int
    repetitions: int
    next_review_date: datetime
    last_reviewed: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True


class FlashcardUpdateSchema(BaseModel):
    """Schema for updating flashcard content"""

    front: Optional[str] = None
    back: Optional[str] = None
    difficulty: Optional[str] = None
    explanation: Optional[str] = None


class FlashcardReviewSchema(BaseModel):
    """Schema for reviewing flashcard (spaced repetition)"""

    confidence: int = Field(..., ge=1, le=5)  # 1-5 stars


class FlashcardTopicSchema(BaseModel):
    """Schema for unique topics"""

    topic: str
    count: int  # Number of flashcards for this topic
    count: int  # Number of flashcards for this topic
