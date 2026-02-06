"""Lesson request/response schemas."""

from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class BoardActionSchema(BaseModel):
    """Board action schema for lesson visualization."""
    type: str
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
        extra = "allow"


class LessonCreateSchema(BaseModel):
    """Lesson creation request."""
    topic: str
    title: str
    narration_script: str
    duration: float
    tailored_to_interest: Optional[str] = None
    audio_url: Optional[str] = None
    board_actions: List[Dict[str, Any]] = Field(default_factory=list)
    raw_llm_output: Optional[Dict[str, Any]] = None


class LessonGenerateSchema(BaseModel):
    """Lesson generation request (for AI generation)."""
    topic: str
    user_interest: str
    proficiency_level: str = "beginner"


class LessonResponseSchema(BaseModel):
    """Lesson response schema."""
    id: Optional[str] = Field(alias="_id")
    topic: str
    title: str
    narration_script: str
    duration: float
    tailored_to_interest: Optional[str] = None
    audio_url: Optional[str] = None
    board_actions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    raw_llm_output: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""
        populate_by_name = True


class LessonListSchema(BaseModel):
    """Lesson list item schema."""
    id: Optional[str] = Field(alias="_id")
    topic: str
    title: str
    tailored_to_interest: Optional[str] = None
    duration: float
    created_at: datetime

    class Config:
        """Pydantic config."""
        populate_by_name = True


class LessonUpdateSchema(BaseModel):
    """Lesson update request."""
    topic: Optional[str] = None
    title: Optional[str] = None
    narration_script: Optional[str] = None
    duration: Optional[float] = None
    tailored_to_interest: Optional[str] = None
    audio_url: Optional[str] = None
    board_actions: Optional[List[Dict[str, Any]]] = None
