"""Lesson request/response schemas."""

from typing import Optional, List, Any, Dict, Union
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
    grade_level: str = "middle school"


class BatchLessonGenerateSchema(BaseModel):
    """Batch lesson generation request for multiple topics."""
    topics: List[str]  # List of topics to generate lessons for
    user_interest: str
    proficiency_level: str = "beginner"
    grade_level: str = "middle school"


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
    batch_id: Optional[str] = None  # Groups lessons generated together
    batch_index: Optional[int] = None  # Position in batch (0, 1, 2...)
    batch_total: Optional[int] = None  # Total lessons in batch

    class Config:
        """Pydantic config."""
        populate_by_name = True


class BatchLessonResponseSchema(BaseModel):
    """Response for batch lesson generation."""
    batch_id: str
    total_lessons: int
    lessons: List[LessonResponseSchema]
    playlist_order: List[str]  # List of lesson IDs in order


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
