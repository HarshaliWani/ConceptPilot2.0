"""User progress request/response schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserProgressCreateSchema(BaseModel):
    """Create user progress."""
    lesson_id: str
    status: str = "not_started"
    mastery_score: float = 0.0
    time_spent_seconds: int = 0


class UserProgressUpdateSchema(BaseModel):
    """Update user progress."""
    status: Optional[str] = None
    mastery_score: Optional[float] = None
    time_spent_seconds: Optional[int] = None


class UserProgressResponseSchema(BaseModel):
    """User progress response schema."""
    id: Optional[str] = Field(alias="_id")
    user_id: str
    lesson_id: str
    status: str
    mastery_score: float
    time_spent_seconds: int
    created_at: datetime
    last_accessed: datetime

    class Config:
        """Pydantic config."""
        populate_by_name = True


class UserProgressListSchema(BaseModel):
    """User progress list item schema."""
    id: Optional[str] = Field(alias="_id")
    lesson_id: str
    status: str
    mastery_score: float
    last_accessed: datetime

    class Config:
        """Pydantic config."""
        populate_by_name = True
