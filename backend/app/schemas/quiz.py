"""Quiz request/response schemas."""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class QuizExplanationSchema(BaseModel):
    """Explanation schema for quiz answers."""
    correct: str
    incorrect: Dict[str, str]


class QuizQuestionSchema(BaseModel):
    """Quiz question schema."""
    id: str
    question: str
    options: List[str]
    correctAnswer: int
    difficulty: str
    explanation: QuizExplanationSchema


class QuizMetadataSchema(BaseModel):
    """Quiz metadata schema."""
    generated_at: datetime
    question_count: int
    topic: str
    topic_description: str


class QuizGenerateSchema(BaseModel):
    """Quiz generation request."""
    lesson_id: Optional[str] = None
    topic: str
    topic_description: str
    user_id: Optional[str] = None


class QuizCreateSchema(BaseModel):
    """Quiz creation request."""
    user_id: Optional[str] = None
    lesson_id: Optional[str] = None
    topic: str
    topic_description: str
    questions: List[QuizQuestionSchema]
    metadata: QuizMetadataSchema


class QuizResponseSchema(BaseModel):
    """Quiz response schema."""
    id: Optional[str] = Field(alias="_id")
    user_id: Optional[str] = None
    lesson_id: Optional[str] = None
    topic: str
    topic_description: str
    questions: List[QuizQuestionSchema]
    metadata: QuizMetadataSchema
    created_at: datetime

    class Config:
        """Pydantic config."""
        populate_by_name = True


class QuizListSchema(BaseModel):
    """Quiz list item schema."""
    id: Optional[str] = Field(alias="_id")
    topic: str
    topic_description: str
    question_count: int
    created_at: datetime

    class Config:
        """Pydantic config."""
        populate_by_name = True


class QuizSubmitSchema(BaseModel):
    """Quiz submission request."""
    user_id: str
    quiz_id: str
    lesson_id: Optional[str] = None
    answers: Dict[str, int]  # question_id -> selected_answer_index
    time_taken_seconds: int


class QuizAttemptResponseSchema(BaseModel):
    """Quiz attempt response schema."""
    id: Optional[str] = Field(alias="_id")
    user_id: str
    quiz_id: str
    lesson_id: Optional[str] = None
    answers: Dict[str, int]
    score: float
    correct_count: int
    wrong_count: int
    time_taken_seconds: int
    completed_at: datetime

    class Config:
        """Pydantic config."""
        populate_by_name = True


class QuizResultSchema(BaseModel):
    """Quiz result summary."""
    quiz_id: str
    attempt_id: str
    score: float
    correct_count: int
    wrong_count: int
    total_questions: int
    time_taken_seconds: int
    passed: bool  # True if score >= 70%
