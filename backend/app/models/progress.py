"""User progress models for MongoDB documents."""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId in Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)

    def __repr__(self):
        return f"ObjectId('{self}')"


class UserProgressBase(BaseModel):
    """Base model for user progress."""
    user_id: PyObjectId
    lesson_id: PyObjectId
    status: str = "not_started"  # not_started, in_progress, completed
    mastery_score: float = 0.0  # 0.0 to 1.0
    time_spent_seconds: int = 0


class UserProgressCreate(UserProgressBase):
    """Create user progress."""
    pass


class UserProgressUpdate(BaseModel):
    """Update user progress."""
    status: Optional[str] = None
    mastery_score: Optional[float] = None
    time_spent_seconds: Optional[int] = None


class UserProgress(UserProgressBase):
    """User progress document model."""
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserProgressResponse(UserProgress):
    """User progress response model for API."""
    pass
