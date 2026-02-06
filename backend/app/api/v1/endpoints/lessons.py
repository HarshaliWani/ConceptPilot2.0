"""Lessons endpoints: generate, get, list."""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.lesson import (
    LessonGenerateSchema,
    LessonResponseSchema,
    LessonListSchema,
    LessonCreateSchema,
)
from app.services.lesson_generator import generate_lesson
from app.db.mongodb import MongoDBOperations
from app.core.database import get_database
from bson import ObjectId

router = APIRouter()


def _normalize_doc(doc: dict) -> dict:
    if not doc:
        return doc
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc


@router.post("/generate", response_model=LessonResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_and_save_lesson(payload: LessonGenerateSchema, db=Depends(get_database)):
    """Generate a lesson via LLM (or fallback) and save to DB."""
    generated = await generate_lesson(payload.topic, payload.user_interest, payload.proficiency_level)

    # Ensure metadata
    if "created_at" not in generated:
        generated["created_at"] = datetime.utcnow()

    ops = MongoDBOperations(db, "lessons")
    inserted_id = await ops.create(generated)
    doc = generated.copy()
    doc["_id"] = inserted_id
    return _normalize_doc(doc)


@router.get("/{lesson_id}", response_model=LessonResponseSchema)
async def get_lesson(lesson_id: str, db=Depends(get_database)):
    ops = MongoDBOperations(db, "lessons")
    doc = await ops.read_by_id(lesson_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return _normalize_doc(doc)


@router.get("/", response_model=List[LessonListSchema])
async def list_lessons(skip: int = 0, limit: int = 20, db=Depends(get_database)):
    ops = MongoDBOperations(db, "lessons")
    docs = await ops.read_many({}, skip=skip, limit=limit, sort_by="created_at", sort_order=-1)
    return [_normalize_doc(d) for d in docs]
