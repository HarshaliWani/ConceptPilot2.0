"""User models for MongoDB documents."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
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


class UserInterestBase(BaseModel):
    """Base model for user interest."""
    interest_category: str
    specific_interest: str
    proficiency_level: str


class UserInterestCreate(UserInterestBase):
    """Create user interest."""
    pass


class UserInterest(UserInterestBase):
    """User interest document model."""
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CustomUserBase(BaseModel):
    """Base model for custom user."""
    email: EmailStr
    name: str
    username: str
    grade_level: Optional[str] = Field(default="middle school")


class CustomUserCreate(CustomUserBase):
    """Create custom user."""
    password: str


class CustomUser(CustomUserBase):
    """Custom user document model."""
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    interests: List[UserInterest] = Field(default_factory=list)

    class Config:
        """Pydantic config."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CustomUserInDB(CustomUser):
    """User model stored in database with hashed password."""
    hashed_password: str


class CustomUserResponse(CustomUser):
    """User response model (without sensitive data)."""
    pass
