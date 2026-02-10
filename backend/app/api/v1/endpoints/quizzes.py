"""Quiz endpoints: generate, get, submit."""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.schemas.quiz import (
    QuizGenerateSchema,
    QuizResponseSchema,
    QuizListSchema,
    QuizSubmitSchema,
    QuizResultSchema,
    QuizAttemptResponseSchema,
)
from app.services.quiz_generator import generate_quiz
from app.db.mongodb import MongoDBOperations
from app.core.database import get_database

router = APIRouter()


def _normalize_doc(doc: dict) -> dict:
    """Normalize MongoDB document to response schema."""
    if not doc:
        return doc
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    if "user_id" in doc and isinstance(doc["user_id"], ObjectId):
        doc["user_id"] = str(doc["user_id"])
    if "lesson_id" in doc and isinstance(doc["lesson_id"], ObjectId):
        doc["lesson_id"] = str(doc["lesson_id"])
    if "quiz_id" in doc and isinstance(doc["quiz_id"], ObjectId):
        doc["quiz_id"] = str(doc["quiz_id"])
    return doc


@router.post("/generate", response_model=QuizResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_and_save_quiz(payload: QuizGenerateSchema, db=Depends(get_database)):
    """Generate a quiz via LLM and save to DB."""
    try:
        # Generate quiz using AI
        generated = await generate_quiz(
            topic=payload.topic,
            topic_description=payload.topic_description
        )
        
        # Prepare document for MongoDB
        quiz_doc = {
            "topic": payload.topic,
            "topic_description": payload.topic_description,
            "questions": generated["questions"],
            "metadata": generated["metadata"],
            "created_at": datetime.utcnow()
        }
        
        # Add optional fields if provided
        if payload.user_id:
            # Try to convert to ObjectId, but store as string if invalid format
            try:
                quiz_doc["user_id"] = ObjectId(payload.user_id)
            except Exception:
                quiz_doc["user_id"] = payload.user_id  # Store as string
        if payload.lesson_id:
            try:
                quiz_doc["lesson_id"] = ObjectId(payload.lesson_id)
            except Exception:
                quiz_doc["lesson_id"] = payload.lesson_id  # Store as string
        
        # Save to database
        ops = MongoDBOperations(db, "quizzes")
        inserted_id = await ops.create(quiz_doc)
        
        quiz_doc["_id"] = inserted_id
        return _normalize_doc(quiz_doc)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[QuizEndpoint] Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")


@router.get("/{quiz_id}", response_model=QuizResponseSchema)
async def get_quiz(quiz_id: str, db=Depends(get_database)):
    """Get a quiz by ID."""
    ops = MongoDBOperations(db, "quizzes")
    doc = await ops.read_by_id(quiz_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return _normalize_doc(doc)


@router.get("/", response_model=List[QuizListSchema])
async def list_quizzes(
    skip: int = 0,
    limit: int = 20,
    user_id: str = None,
    lesson_id: str = None,
    db=Depends(get_database)
):
    """List quizzes with optional filters."""
    ops = MongoDBOperations(db, "quizzes")
    
    # Build query
    query = {}
    if user_id:
        query["user_id"] = ObjectId(user_id)
    if lesson_id:
        query["lesson_id"] = ObjectId(lesson_id)
    
    docs = await ops.read_many(
        query=query,
        skip=skip,
        limit=limit,
        sort_by="created_at",
        sort_order=-1
    )
    
    # Transform to list schema
    list_items = []
    for doc in docs:
        list_item = {
            "_id": doc["_id"],
            "topic": doc["topic"],
            "topic_description": doc["topic_description"],
            "question_count": len(doc.get("questions", [])),
            "created_at": doc["created_at"]
        }
        list_items.append(_normalize_doc(list_item))
    
    return list_items


@router.post("/{quiz_id}/submit", response_model=QuizResultSchema)
async def submit_quiz(quiz_id: str, payload: QuizSubmitSchema, db=Depends(get_database)):
    """Submit quiz answers and calculate score."""
    # Get the quiz
    quiz_ops = MongoDBOperations(db, "quizzes")
    quiz_doc = await quiz_ops.read_by_id(quiz_id)
    if not quiz_doc:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score and proficiency metrics
    questions = quiz_doc["questions"]
    total_questions = len(questions)
    correct_count = 0
    wrong_count = 0
    
    # Proficiency tracking by difficulty
    difficulty_weights = {"easy": 0.5, "medium": 1.0, "hard": 1.5}
    proficiency_score = 0.0
    max_proficiency_score = 0.0
    
    for question in questions:
        q_id = question["id"]
        difficulty = question.get("difficulty", "medium").lower()
        weight = difficulty_weights.get(difficulty, 1.0)
        max_proficiency_score += weight
        
        if q_id in payload.answers:
            user_answer = payload.answers[q_id]
            correct_answer = question["correctAnswer"]
            if user_answer == correct_answer:
                correct_count += 1
                proficiency_score += weight
            else:
                wrong_count += 1
    
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    passed = score >= 70.0
    
    # Calculate normalized proficiency (0.0 to 1.0)
    normalized_proficiency = proficiency_score / max_proficiency_score if max_proficiency_score > 0 else 0.0
    
    # Create attempt record
    attempt_doc = {
        "user_id": payload.user_id,  # Store as-is (string or ObjectId)
        "quiz_id": ObjectId(quiz_id),
        "answers": {k: v for k, v in payload.answers.items()},  # Convert to regular dict
        "score": score,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "time_taken_seconds": payload.time_taken_seconds,
        "completed_at": datetime.utcnow(),
        "proficiency_score": normalized_proficiency
    }
    
    if payload.lesson_id:
        try:
            attempt_doc["lesson_id"] = ObjectId(payload.lesson_id)
        except Exception:
            attempt_doc["lesson_id"] = payload.lesson_id
    
    # Save attempt
    attempt_ops = MongoDBOperations(db, "quiz_attempts")
    attempt_id = await attempt_ops.create(attempt_doc)
    
    # Update user proficiency for this topic
    try:
        user_ops = MongoDBOperations(db, "users")
        # Try ObjectId lookup first, then fallback to string ID lookup
        user_doc = await user_ops.read_by_id(payload.user_id)
        if not user_doc:
            # If ObjectId lookup failed, try direct string ID query
            user_doc = await user_ops.collection.find_one({"_id": payload.user_id})
        
        if user_doc:
            # Get current topic proficiency
            topic_proficiency = user_doc.get("topic_proficiency", {})
            topic = quiz_doc["topic"]
            
            # Calculate running average (weighted towards recent performance)
            if topic in topic_proficiency:
                current_prof = topic_proficiency[topic]
                # 70% current + 30% new score
                updated_prof = (current_prof * 0.7) + (normalized_proficiency * 0.3)
            else:
                updated_prof = normalized_proficiency
            
            # Update topic proficiency
            topic_proficiency[topic] = round(updated_prof, 4)
            
            # Update user document - try update method first, fallback to direct collection update
            try:
                updated = await user_ops.update(
                    payload.user_id,
                    {"topic_proficiency": topic_proficiency}
                )
                if not updated:
                    # Fallback to direct collection update for string IDs
                    result = await user_ops.collection.update_one(
                        {"_id": payload.user_id},
                        {"$set": {"topic_proficiency": topic_proficiency}}
                    )
                    updated = result.modified_count > 0
            except Exception:
                # Direct collection update for non-ObjectId _id
                result = await user_ops.collection.update_one(
                    {"_id": payload.user_id},
                    {"$set": {"topic_proficiency": topic_proficiency}}
                )
                updated = result.modified_count > 0
            
            if updated:
                print(f"[QuizSubmit] Updated proficiency for user {payload.user_id}, topic '{topic}': {updated_prof:.4f}")
            else:
                print(f"[QuizSubmit] Warning: Failed to update proficiency for user {payload.user_id}")
        else:
            print(f"[QuizSubmit] User {payload.user_id} not found, skipping proficiency update")
    
    except Exception as e:
        # Log error but don't fail the quiz submission
        print(f"[QuizSubmit] Error updating user proficiency: {e}")
    
    # Return result
    return QuizResultSchema(
        quiz_id=quiz_id,
        attempt_id=str(attempt_id),
        score=score,
        correct_count=correct_count,
        wrong_count=wrong_count,
        total_questions=total_questions,
        time_taken_seconds=payload.time_taken_seconds,
        passed=passed
    )


@router.get("/attempts/user/{user_id}", response_model=List[QuizAttemptResponseSchema])
async def get_user_quiz_attempts(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    db=Depends(get_database)
):
    """Get quiz attempts for a specific user."""
    ops = MongoDBOperations(db, "quiz_attempts")
    
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    
    docs = await ops.read_many(
        query={"user_id": user_obj_id},
        skip=skip,
        limit=limit,
        sort_by="completed_at",
        sort_order=-1
    )
    
    return [_normalize_doc(doc) for doc in docs]
