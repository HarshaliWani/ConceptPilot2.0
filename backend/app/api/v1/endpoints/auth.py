"""Authentication endpoints: register and login."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.schemas.user import (
    UserRegisterSchema,
    UserLoginSchema,
    UserResponseSchema,
    TokenSchema,
)
from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.mongodb import MongoDBOperations
from app.core.database import get_database

router = APIRouter()


def _normalize_user(doc: dict) -> dict:
    """Normalize MongoDB document to response schema."""
    if not doc:
        return doc
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    # Remove password hash from response
    doc.pop("password_hash", None)
    return doc


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterSchema, db=Depends(get_database)):
    """Register a new user."""
    ops = MongoDBOperations(db, "users")

    # Check if user with this email already exists
    existing = await ops.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username already exists
    existing_user = await ops.find_one({"username": payload.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Hash the password
    password_hash = get_password_hash(payload.password)

    # Create new user document
    user_doc = {
        "email": payload.email,
        "name": payload.name,
        "username": payload.username,
        "password_hash": password_hash,
        "interests": [],
        "created_at": datetime.utcnow(),
    }

    # Insert into database
    inserted_id = await ops.create(user_doc)
    user_doc["_id"] = inserted_id

    return _normalize_user(user_doc)


@router.post("/login", response_model=TokenSchema)
async def login(payload: UserLoginSchema, db=Depends(get_database)):
    """Login with email and password, return JWT token."""
    ops = MongoDBOperations(db, "users")

    # Find user by email
    user_doc = await ops.find_one({"email": payload.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(payload.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    access_token = create_access_token(data={"sub": payload.email})

    return {"access_token": access_token, "token_type": "bearer"}
