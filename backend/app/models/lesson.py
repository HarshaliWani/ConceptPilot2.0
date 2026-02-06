"""Lesson models for MongoDB documents."""

from typing import Optional, List, Any, Dict
from datetime import datetime
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


class BoardAction(BaseModel):
    """Individual board action for lesson visualization."""
    type: str  # e.g., 'text', 'line', 'rect', 'circle', 'svg_path'
    timestamp: float
    content: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    points: Optional[List[List[float]]] = None
    stroke: Optional[str] = None
    strokeWidth: Optional[float] = None
    fill: Optional[str] = None
    radius: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    fontSize: Optional[int] = None
    data: Optional[str] = None  # for svg_path
    
    class Config:
        """Pydantic config."""
        extra = "allow"  # Allow additional fields


class LessonBase(BaseModel):
    """Base model for lesson."""
    topic: str
    title: str
    narration_script: str
    duration: float
    tailored_to_interest: Optional[str] = None
    audio_url: Optional[str] = None
    board_actions: List[Dict[str, Any]] = Field(default_factory=list)


class LessonCreate(LessonBase):
    """Create lesson."""
    raw_llm_output: Optional[Dict[str, Any]] = None


class Lesson(LessonBase):
    """Lesson document model."""
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    raw_llm_output: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class LessonResponse(Lesson):
    """Lesson response model for API."""
    pass


class LessonListResponse(BaseModel):
    """Lesson list response."""
    id: Optional[PyObjectId] = Field(alias="_id")
    topic: str
    title: str
    tailored_to_interest: Optional[str] = None
    duration: float
    created_at: datetime

    class Config:
        """Pydantic config."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
