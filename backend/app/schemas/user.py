"""User request/response schemas."""

from typing import Optional, List
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


class UserLoginSchema(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserUpdateSchema(BaseModel):
    """User update request."""
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponseSchema(BaseModel):
    """User response schema."""
    id: Optional[str] = Field(alias="_id")
    email: str
    name: str
    username: str
    interests: List[UserInterestResponseSchema] = Field(default_factory=list)

    class Config:
        """Pydantic config."""
        populate_by_name = True


class TokenSchema(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenDataSchema(BaseModel):
    """Token payload data."""
    email: Optional[str] = None
