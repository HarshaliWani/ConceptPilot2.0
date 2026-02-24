# backend/app/api/v1/endpoints/flashcards.py
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from bson import ObjectId

from ....core.database import get_database
from ....core.security import decode_access_token
from ....db.mongodb import MongoDBOperations
from ....schemas.flashcard import (
    FlashcardGenerateRequestSchema,
    FlashcardCreateSchema,
    FlashcardResponseSchema,
    FlashcardUpdateSchema,
    FlashcardReviewSchema,
    FlashcardTopicSchema
)
from ....services.flashcard_generator import generate_flashcards

router = APIRouter()


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract user ID from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_access_token(token)
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user ID from database
        db = await get_database()
        ops = MongoDBOperations(db, "users")
        user = await ops.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return str(user["_id"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def calculate_next_review(confidence: int, ease_factor: float, interval: int, repetitions: int):
    """
    SM-2 Spaced Repetition Algorithm
    
    Args:
        confidence: User rating 1-5 (1=worst, 5=best)
        ease_factor: Current ease factor (starts at 2.5)
        interval: Current interval in days
        repetitions: Number of successful reviews
        
    Returns:
        (new_ease_factor, new_interval, new_repetitions, next_review_date)
    """
    # Convert 1-5 confidence to 0-5 quality (SM-2 expects 0-5)
    quality = confidence - 1
    
    if quality < 3:
        # Failed review - restart
        new_repetitions = 0
        new_interval = 1
        new_ease_factor = ease_factor
    else:
        # Successful review
        new_repetitions = repetitions + 1
        
        # Calculate new ease factor
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if new_ease_factor < 1.3:
            new_ease_factor = 1.3
        
        # Calculate new interval
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(interval * new_ease_factor)
    
    next_review_date = datetime.utcnow() + timedelta(days=new_interval)
    
    return new_ease_factor, new_interval, new_repetitions, next_review_date


def _normalize_flashcard(doc: dict) -> dict:
    """Convert MongoDB document _id to string id"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.post("/generate", response_model=List[FlashcardResponseSchema])
async def generate_and_save_flashcards(
    request: FlashcardGenerateRequestSchema,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Generate 10 flashcards using LLM and save to database"""
    try:
        # Generate flashcards using LLM
        generated = await generate_flashcards(request.topic, count=10)
        
        # Save to database
        ops = MongoDBOperations(db, "flashcards")
        saved_flashcards = []
        
        for card_data in generated:
            flashcard_doc = {
                "user_id": user_id,
                "topic": request.topic,
                "front": card_data["front"],
                "back": card_data["back"],
                "difficulty": card_data["difficulty"],
                "explanation": card_data.get("explanation"),
                "confidence": 0,
                "ease_factor": 2.5,
                "interval": 0,
                "repetitions": 0,
                "next_review_date": datetime.utcnow(),  # Available for review immediately
                "last_reviewed": None,
                "created_at": datetime.utcnow()
            }
            
            inserted_id = await ops.create(flashcard_doc)
            flashcard_doc["_id"] = inserted_id
            saved_flashcards.append(_normalize_flashcard(flashcard_doc))
        
        return saved_flashcards
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")


@router.get("/", response_model=List[FlashcardResponseSchema])
async def get_flashcards(
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    due_for_review: bool = False,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get flashcards with optional filters"""
    ops = MongoDBOperations(db, "flashcards")
    
    # Build filter query
    query = {"user_id": user_id}
    if topic:
        query["topic"] = topic
    if difficulty:
        query["difficulty"] = difficulty
    if due_for_review:
        query["next_review_date"] = {"$lte": datetime.utcnow()}
    
    flashcards = await ops.find_many(query)
    return [_normalize_flashcard(fc) for fc in flashcards]


@router.get("/topics", response_model=List[FlashcardTopicSchema])
async def get_topics(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get list of unique topics with flashcard counts"""
    ops = MongoDBOperations(db, "flashcards")
    
    # Aggregate topics
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$topic",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    collection = db["flashcards"]
    results = await collection.aggregate(pipeline).to_list(length=None)
    
    return [
        {"topic": result["_id"], "count": result["count"]}
        for result in results
    ]


@router.get("/{flashcard_id}", response_model=FlashcardResponseSchema)
async def get_flashcard(
    flashcard_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get a single flashcard by ID"""
    ops = MongoDBOperations(db, "flashcards")
    
    try:
        flashcard = await ops.find_one({
            "_id": ObjectId(flashcard_id),
            "user_id": user_id
        })
        
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        return _normalize_flashcard(flashcard)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid flashcard ID: {str(e)}")


@router.put("/{flashcard_id}/review", response_model=FlashcardResponseSchema)
async def review_flashcard(
    flashcard_id: str,
    review: FlashcardReviewSchema,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Update flashcard after review (spaced repetition)"""
    ops = MongoDBOperations(db, "flashcards")
    
    try:
        # Get current flashcard
        flashcard = await ops.find_one({
            "_id": ObjectId(flashcard_id),
            "user_id": user_id
        })
        
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        # Calculate next review using SM-2 algorithm
        ease_factor, interval, repetitions, next_review_date = calculate_next_review(
            confidence=review.confidence,
            ease_factor=flashcard["ease_factor"],
            interval=flashcard["interval"],
            repetitions=flashcard["repetitions"]
        )
        
        # Update flashcard
        updates = {
            "confidence": review.confidence,
            "ease_factor": ease_factor,
            "interval": interval,
            "repetitions": repetitions,
            "next_review_date": next_review_date,
            "last_reviewed": datetime.utcnow()
        }
        
        await ops.update(str(flashcard["_id"]), updates)
        
        # Return updated flashcard
        updated = await ops.find_one({"_id": ObjectId(flashcard_id)})
        return _normalize_flashcard(updated)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to review flashcard: {str(e)}")


@router.put("/{flashcard_id}", response_model=FlashcardResponseSchema)
async def update_flashcard(
    flashcard_id: str,
    update_data: FlashcardUpdateSchema,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Update flashcard content"""
    ops = MongoDBOperations(db, "flashcards")
    
    try:
        # Verify ownership
        flashcard = await ops.find_one({
            "_id": ObjectId(flashcard_id),
            "user_id": user_id
        })
        
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        # Build updates
        updates = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        await ops.update(str(flashcard["_id"]), updates)
        
        # Return updated flashcard
        updated = await ops.find_one({"_id": ObjectId(flashcard_id)})
        return _normalize_flashcard(updated)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update flashcard: {str(e)}")


@router.delete("/{flashcard_id}")
async def delete_flashcard(
    flashcard_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Delete a flashcard"""
    ops = MongoDBOperations(db, "flashcards")
    
    try:
        # Verify ownership
        flashcard = await ops.find_one({
            "_id": ObjectId(flashcard_id),
            "user_id": user_id
        })
        
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        await ops.delete(str(flashcard["_id"]))
        
        return {"message": "Flashcard deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete flashcard: {str(e)}")
