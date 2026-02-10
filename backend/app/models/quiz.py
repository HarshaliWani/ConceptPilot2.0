"""Quiz models for MongoDB documents."""

from typing import Optional, List, Dict, Any
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


class QuizExplanation(BaseModel):
    """Explanation for quiz question answers."""
    correct: str
    incorrect: Dict[str, str]  # Map of option index to explanation

    class Config:
        """Pydantic config."""
        extra = "allow"


class QuizQuestion(BaseModel):
    """Individual quiz question."""
    id: str
    question: str
    options: List[str]  # List of 4 options
    correctAnswer: int  # Index of correct answer (0-3)
    difficulty: str  # "easy", "medium", or "hard"
    explanation: QuizExplanation

    class Config:
        """Pydantic config."""
        extra = "allow"


class QuizMetadata(BaseModel):
    """Quiz metadata."""
    generated_at: datetime
    question_count: int
    topic: str
    topic_description: str


class QuizBase(BaseModel):
    """Base model for quiz."""
    user_id: Optional[PyObjectId] = None
    lesson_id: Optional[PyObjectId] = None
    topic: str
    topic_description: str
    questions: List[QuizQuestion] = Field(default_factory=list)


class QuizCreate(QuizBase):
    """Create quiz."""
    metadata: Optional[QuizMetadata] = None


class Quiz(QuizBase):
    """Quiz document model."""
    id: Optional[PyObjectId] = Field(alias="_id")
    metadata: QuizMetadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class QuizResponse(Quiz):
    """Quiz response model for API."""
    pass


class QuizAttemptBase(BaseModel):
    """Base model for quiz attempt."""
    user_id: PyObjectId
    quiz_id: PyObjectId
    lesson_id: Optional[PyObjectId] = None
    answers: Dict[str, int]  # Map of question_id to selected answer index
    score: float
    correct_count: int
    wrong_count: int
    time_taken_seconds: int


class QuizAttemptCreate(QuizAttemptBase):
    """Create quiz attempt."""
    pass


class QuizAttempt(QuizAttemptBase):
    """Quiz attempt document model."""
    id: Optional[PyObjectId] = Field(alias="_id")
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class QuizAttemptResponse(QuizAttempt):
    """Quiz attempt response model for API."""
    pass
