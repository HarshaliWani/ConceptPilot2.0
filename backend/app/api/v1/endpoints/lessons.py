"""Lessons endpoints: generate, get, list."""
from datetime import datetime
from typing import List, AsyncGenerator
import os
import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas.lesson import (
    LessonGenerateSchema,
    LessonResponseSchema,
    LessonListSchema,
    LessonCreateSchema,
    BatchLessonGenerateSchema,
    BatchLessonResponseSchema,
)
from app.services.lesson_generator import generate_lesson, _clean_narration_for_tts
from app.services.tts_service import generate_audio_stream
from app.services.audio_timestamps import extract_word_timestamps, map_timestamps_to_board_actions
from app.db.mongodb import MongoDBOperations
from app.core.database import get_database
from bson import ObjectId

router = APIRouter()


def _normalize_doc(doc: dict) -> dict:
    """Normalize MongoDB document for JSON serialization."""
    if not doc:
        return doc
    
    # Convert ObjectId to string
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    
    # Convert all datetime fields to ISO strings
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
    
    return doc


@router.post("/generate", response_model=LessonResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_and_save_lesson(payload: LessonGenerateSchema, db=Depends(get_database)):
    """Generate a lesson via LLM (or fallback) and save to DB."""
    generated = await generate_lesson(payload.topic, payload.user_interest, payload.proficiency_level, payload.grade_level)

    # Ensure metadata
    if "created_at" not in generated:
        generated["created_at"] = datetime.utcnow()

    ops = MongoDBOperations(db, "lessons")
    inserted_id = await ops.create(generated)
    doc = generated.copy()
    doc["_id"] = inserted_id
    return _normalize_doc(doc)


@router.post("/generate/batch", response_model=BatchLessonResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_batch_lessons(payload: BatchLessonGenerateSchema, db=Depends(get_database)):
    """
    Generate multiple lessons sequentially for a playlist.
    
    This endpoint creates a batch of lessons for multiple topics, perfect for:
    - Teaching related concepts in sequence
    - Creating learning playlists
    - Multi-part lessons
    
    The lessons are linked with a batch_id and can be played sequentially
    in the frontend with auto-advance.
    
    Example request:
        {
            "topics": ["photosynthesis", "cellular respiration", "osmosis"],
            "user_interest": "basketball",
            "proficiency_level": "beginner",
            "grade_level": "middle school"
        }
    
    Returns:
        {
            "batch_id": "uuid-here",
            "total_lessons": 3,
            "lessons": [...],
            "playlist_order": ["id1", "id2", "id3"]
        }
    """
    if not payload.topics or len(payload.topics) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one topic is required"
        )
    
    # Generate unique batch ID
    batch_id = str(uuid.uuid4())
    batch_total = len(payload.topics)
    
    print(f"[BatchGenerate] Starting batch {batch_id} for {batch_total} topics")
    
    lessons = []
    playlist_order = []
    ops = MongoDBOperations(db, "lessons")
    
    for index, topic in enumerate(payload.topics):
        print(f"[BatchGenerate] Generating lesson {index + 1}/{batch_total}: {topic}")
        
        try:
            # Generate lesson
            generated = await generate_lesson(
                topic,
                payload.user_interest,
                payload.proficiency_level,
                payload.grade_level
            )
            
            # Add batch metadata
            generated["batch_id"] = batch_id
            generated["batch_index"] = index
            generated["batch_total"] = batch_total
            generated["created_at"] = datetime.utcnow()
            
            # Save to database
            inserted_id = await ops.create(generated)
            doc = generated.copy()
            doc["_id"] = inserted_id
            
            normalized = _normalize_doc(doc)
            lessons.append(normalized)
            playlist_order.append(normalized["_id"])
            
            print(f"[BatchGenerate] ✓ Lesson {index + 1} saved: {normalized['_id']}")
            
        except Exception as e:
            print(f"[BatchGenerate] ✗ Failed to generate lesson for '{topic}': {e}")
            # Continue with other topics instead of failing entire batch
            continue
    
    if not lessons:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate any lessons in batch"
        )
    
    print(f"[BatchGenerate] ✅ Batch complete: {len(lessons)}/{batch_total} lessons generated")
    
    return {
        "batch_id": batch_id,
        "total_lessons": len(lessons),
        "lessons": lessons,
        "playlist_order": playlist_order
    }


@router.get("/generate/batch/stream")
async def generate_batch_lessons_stream(
    topics: str,  # Comma-separated topics
    user_interest: str = "general interests",
    proficiency_level: str = "beginner",
    grade_level: str = "middle school",
    db=Depends(get_database)
):
    """
    Stream lessons progressively as they're generated using Server-Sent Events (SSE).
    
    This dramatically improves UX by showing the first lesson in ~3-4 minutes
    instead of waiting 20+ minutes for all lessons to complete.
    
    Each lesson is sent as an SSE event as soon as it's ready:
    - User can start watching lesson 1 immediately
    - Lessons 2-6 queue up in the playlist
    - Total perceived wait time: 4 min vs 20+ min
    
    Query parameters:
        topics: Comma-separated list of topics (e.g., "photosynthesis,respiration,osmosis")
        user_interest: User's hobby/interest for personalization (default: "general interests")
        proficiency_level: Learning level (default: "beginner")
        grade_level: Grade level (default: "middle school")
    
    SSE Format:
        event: lesson
        data: {"_id": "...", "title": "...", ...}
        
        event: complete
        data: {"batch_id": "...", "total": 3}
        
        event: error
        data: {"topic": "...", "error": "..."}
    
    Example usage:
        const eventSource = new EventSource('/api/v1/lessons/generate/batch/stream?topics=photosynthesis,respiration');
        eventSource.addEventListener('lesson', (e) => {
            const lesson = JSON.parse(e.data);
        });
    """
    # Parse comma-separated topics
    topic_list = [t.strip() for t in topics.split(',') if t.strip()]
    
    if not topic_list:
        raise HTTPException(status_code=400, detail="At least one topic is required")
    
    async def lesson_stream() -> AsyncGenerator[str, None]:
        batch_id = str(uuid.uuid4())
        batch_total = len(topic_list)
        
        print(f"[BatchStream] Starting batch {batch_id} for {batch_total} topics")
        
        ops = MongoDBOperations(db, "lessons")
        success_count = 0
        
        for index, topic in enumerate(topic_list):
            print(f"[BatchStream] Generating lesson {index + 1}/{batch_total}: {topic}")
            
            try:
                # Generate lesson (includes LLM + TTS)
                generated = await generate_lesson(
                    topic,
                    user_interest,
                    proficiency_level,
                    grade_level
                )
                
                # Add batch metadata
                generated["batch_id"] = batch_id
                generated["batch_index"] = index
                generated["batch_total"] = batch_total
                generated["created_at"] = datetime.utcnow()
                
                # Save to database
                inserted_id = await ops.create(generated)
                doc = generated.copy()
                doc["_id"] = str(inserted_id)
                
                # Normalize and stream immediately
                normalized = _normalize_doc(doc)
                success_count += 1
                
                # Send lesson as SSE event
                yield f"event: lesson\ndata: {json.dumps(normalized)}\n\n"
                
                print(f"[BatchStream] ✓ Lesson {index + 1} streamed: {normalized['_id']}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"[BatchStream] ✗ Failed to generate '{topic}': {error_msg}")
                
                # Send error event but continue
                yield f"event: error\ndata: {json.dumps({'topic': topic, 'error': error_msg})}\n\n"
                continue
        
        # Send completion event
        completion_data = {
            "batch_id": batch_id,
            "total": success_count,
            "requested": batch_total
        }
        yield f"event: complete\ndata: {json.dumps(completion_data)}\n\n"
        
        print(f"[BatchStream] ✅ Stream complete: {success_count}/{batch_total} lessons")
    
    return StreamingResponse(
        lesson_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


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


# ============================================================================
# STREAMING AUDIO ENDPOINT
# ============================================================================

@router.get("/{lesson_id}/audio/stream")
async def stream_lesson_audio(lesson_id: str, db=Depends(get_database)):
    """
    Stream audio for a lesson in real-time.
    
    This endpoint streams audio chunks as they're generated by Deepgram TTS,
    allowing the frontend to start playback immediately without waiting for
    the entire audio file to be generated.
    
    Benefits:
    - Reduces perceived latency from 60s to <3s
    - Audio starts playing while still being generated
    - Better user experience with immediate feedback
    
    Frontend usage example:
        const audio = new Audio(`/api/v1/lessons/${lessonId}/audio/stream`);
        audio.play(); // Starts playing immediately as data arrives
        
    Or with fetch:
        const response = await fetch(`/api/v1/lessons/${lessonId}/audio/stream`);
        const reader = response.body.getReader();
        // Process chunks as they arrive
    
    Args:
        lesson_id: The lesson ID to stream audio for
        db: Database dependency
        
    Returns:
        StreamingResponse with audio/mpeg content
    """
    # Get lesson from database
    ops = MongoDBOperations(db, "lessons")
    lesson = await ops.read_by_id(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Get narration script
    narration = lesson.get("narration_script", "")
    if not narration:
        raise HTTPException(
            status_code=400, 
            detail="Lesson has no narration script"
        )
    
    # Clean narration for TTS (remove drawing instructions)
    clean_narration = _clean_narration_for_tts(narration)
    
    # Stream audio chunks
    return StreamingResponse(
        generate_audio_stream(clean_narration, lesson_id),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
            "Accept-Ranges": "none"
        }
    )


# ============================================================================
# WORD TIMESTAMPS ENDPOINT
# ============================================================================

@router.get("/{lesson_id}/timestamps")
async def get_word_timestamps(lesson_id: str, db=Depends(get_database)):
    """
    Extract word-level timestamps from lesson audio using Groq Whisper.
    
    This endpoint enables PERFECT synchronization between audio playback and
    canvas animations by providing precise timing for each spoken word.
    
    Benefits:
    - Word-level precision for canvas element highlighting
    - Automatic board action timing adjustment
    - Free to use (Groq Whisper API)
    - Enables karaoke-style word highlighting
    
    Frontend usage example:
        const { word_timestamps, duration } = await fetch(
            `/api/v1/lessons/${lessonId}/timestamps`
        ).then(r => r.json());
        
        // Sync canvas with audio
        audio.addEventListener('timeupdate', () => {
            const currentWord = word_timestamps.find(
                w => w.start <= audio.currentTime && w.end >= audio.currentTime
            );
            if (currentWord) highlightWord(currentWord.word);
        });
    
    Use cases:
    - Highlight text as it's spoken
    - Sync board actions with exact audio timing
    - Create karaoke-style narration display
    - Adjust LLM-generated timestamps to match actual audio
    
    Args:
        lesson_id: The lesson ID to get timestamps for
        db: Database dependency
        
    Returns:
        {
            "lesson_id": "...",
            "audio_url": "/static/audio/lesson123.mp3",
            "duration": 45.2,
            "word_count": 87,
            "word_timestamps": [
                {"word": "Today", "start": 0.0, "end": 0.4},
                {"word": "we'll", "start": 0.5, "end": 0.8},
                ...
            ],
            "board_actions_synced": [...] // Board actions with adjusted timing
        }
    """
    # Get lesson from database
    ops = MongoDBOperations(db, "lessons")
    lesson = await ops.read_by_id(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if audio URL exists
    audio_url = lesson.get("audio_url")
    if not audio_url:
        raise HTTPException(
            status_code=400,
            detail="Lesson has no audio. Generate audio first using /audio/stream endpoint."
        )
    
    # Handle playlist audio (chunked TTS)
    if audio_url.endswith('_playlist.json'):
        # For playlist, use the first chunk's audio file
        playlist_filename = audio_url.split("/")[-1]
        playlist_path = os.path.join("app", "static", "audio", playlist_filename)
        
        if not os.path.exists(playlist_path):
            raise HTTPException(
                status_code=404,
                detail=f"Playlist file not found: {playlist_filename}"
            )
        
        # Load playlist to get first chunk
        import json as json_lib
        with open(playlist_path, 'r') as f:
            playlist_data = json_lib.load(f)
        
        if not playlist_data.get('chunks') or len(playlist_data['chunks']) == 0:
            raise HTTPException(
                status_code=500,
                detail="Playlist has no audio chunks"
            )
        
        # Use first chunk for timestamp extraction
        first_chunk_file = playlist_data['chunks'][0]['file']
        audio_filename = first_chunk_file.split("/")[-1]
        audio_path = os.path.join("app", "static", "audio", audio_filename)
        
        print(f"[Timestamps] Using first chunk of playlist: {audio_filename}")
    else:
        # Single audio file
        audio_filename = audio_url.split("/")[-1]
        audio_path = os.path.join("app", "static", "audio", audio_filename)
    
    # Check if audio file exists
    if not os.path.exists(audio_path):
        raise HTTPException(
            status_code=404,
            detail=f"Audio file not found: {audio_filename}. Generate audio first."
        )
    
    # Extract word timestamps using Groq Whisper
    try:
        print(f\"[Timestamps] Extracting timestamps from: {audio_path}\")
        word_timestamps = await extract_word_timestamps(audio_path)
        
        if word_timestamps is None:
            raise HTTPException(
                status_code=500,
                detail=\"Failed to extract timestamps. Check Groq API key configuration.\"
            )
        
        if not word_timestamps:
            raise HTTPException(
                status_code=500,
                detail=\"No words found in audio transcription.\"
            )
        
        print(f\"[Timestamps] Extracted {len(word_timestamps)} word timestamps\")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f\"[Timestamps] Error extracting timestamps: {str(e)}\")
        raise HTTPException(
            status_code=500,
            detail=f\"Timestamp extraction failed: {str(e)}\"
        )
    
    # Calculate total duration from timestamps
    duration = word_timestamps[-1]["end"] if word_timestamps else 0
    
    # Optionally sync board actions with actual audio timing
    board_actions = lesson.get("board_actions", [])
    synced_board_actions = map_timestamps_to_board_actions(
        word_timestamps, 
        board_actions
    ) if board_actions else []
    
    # Update lesson in database with timestamps and synced actions
    await ops.update(
        lesson_id,
        {
            "word_timestamps": word_timestamps,
            "duration": duration,
            "board_actions": synced_board_actions if synced_board_actions else board_actions,
            "timestamps_extracted_at": datetime.utcnow()
        }
    )
    
    return {
        "lesson_id": lesson_id,
        "audio_url": audio_url,
        "duration": duration,
        "word_count": len(word_timestamps),
        "word_timestamps": word_timestamps,
        "board_actions_synced": synced_board_actions,
        "message": f"Extracted {len(word_timestamps)} word timestamps. Board actions synced to audio timing."
    }

