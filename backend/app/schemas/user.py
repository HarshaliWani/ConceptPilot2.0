"""User request/response schemas."""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserInterestSchema(BaseModel):
    """User interest schema."""

    interest_category: str
    specific_interest: str
    proficiency_level: str


class UserInterestResponseSchema(UserInterestSchema):
    """User interest response."""

    id: Optional[str] = Field(alias="_id")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class UserRegisterSchema(BaseModel):
    """User registration request."""

    email: EmailStr
    name: str
    username: str
    password: str
    grade_level: Optional[str] = Field(default="middle school")
    hobby: Optional[str] = None  # Optional: capture during registration for better personalization


class UserLoginSchema(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class UserUpdateSchema(BaseModel):
    """User update request."""

    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    grade_level: Optional[str] = None
    hobby: Optional[str] = None
    course_code: Optional[str] = None
    year: Optional[int] = None


class UserResponseSchema(BaseModel):
    """User response schema."""

    id: Optional[str] = Field(alias="_id")
    email: str
    name: str
    username: str
    grade_level: Optional[str] = Field(default="middle school")
    hobby: Optional[str] = None
    course_code: Optional[str] = None
    year: Optional[int] = None
    # NOTE: interests field is deprecated - keeping for backward compatibility only
    interests: List[UserInterestResponseSchema] = Field(default_factory=list)
    topic_proficiency: Optional[dict] = Field(default_factory=dict)  # Quiz performance by topic

    class Config:
        """Pydantic config."""

        populate_by_name = True


class TokenSchema(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponseSchema] = None


class TokenDataSchema(BaseModel):
    """Token payload data."""

    email: Optional[str] = None
    email: Optional[str] = None
