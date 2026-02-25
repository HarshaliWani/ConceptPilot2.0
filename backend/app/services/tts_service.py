"""Text-to-speech service using Deepgram API."""

import os
import asyncio
import re
from typing import Optional, Tuple, AsyncGenerator, List, Dict
from deepgram import DeepgramClient
from app.core.config import get_settings
from mutagen.mp3 import MP3

settings = get_settings()


def chunk_text_by_sentences(text: str, max_chars: int = 1900) -> List[str]:
    """
    Split text into chunks at sentence boundaries, respecting character limit.
    
    Args:
        text: Full text to split
        max_chars: Maximum characters per chunk (default 1900 for Deepgram safety margin)
        
    Returns:
        List of text chunks, each under max_chars and ending at sentence boundaries
        
    Example:
        >>> text = "First sentence. Second sentence. Third sentence."
        >>> chunks = chunk_text_by_sentences(text, max_chars=30)
        >>> # Returns: ["First sentence. Second sentence.", "Third sentence."]
    """
    if len(text) <= max_chars:
        return [text]
    
    # Split on sentence boundaries (. ! ?) followed by space or end
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If adding this sentence would exceed limit, save current chunk and start new one
        if current_chunk and len(current_chunk) + len(sentence) + 1 > max_chars:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            # Add sentence to current chunk
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    print(f"[TTS-Chunking] Split {len(text)} chars into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"[TTS-Chunking]   Chunk {i+1}: {len(chunk)} chars")
    
    return chunks


async def generate_audio_stream(text: str, lesson_id: str) -> AsyncGenerator[bytes, None]:
    """
    Stream audio chunks from Deepgram TTS in real-time.
    
    This allows the frontend to start playing audio immediately without waiting
    for the entire file to be generated. Reduces perceived latency from 60s to <3s.
    
    Args:
        text: Text to convert to speech
        lesson_id: Unique identifier for caching/reference
        
    Yields:
        bytes: Audio data chunks as they're generated
        
    Example usage in endpoint:
        return StreamingResponse(
            generate_audio_stream(narration, lesson_id),
            media_type="audio/mpeg"
        )
    """
    api_key = settings.deepgram_api_key
    if not api_key:
        print("[TTS-Stream] No Deepgram API key found")
        return
    
    # Truncate text to Deepgram's limit
    max_chars = 1950
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
        print(f"[TTS-Stream] Text truncated to {max_chars} characters")
    
    try:
        print(f"[TTS-Stream] Starting streaming audio generation for lesson {lesson_id}")
        print(f"[TTS-Stream] Text length: {len(text)} characters")
        
        deepgram = DeepgramClient(api_key=api_key)
        
        # Create directory for optional caching
        audio_dir = "app/static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generate audio - the response is already a generator
        response = deepgram.speak.v1.audio.generate(
            text=text,
            model="aura-2-odysseus-en"
        )
        
        # Optional: Save to file while streaming for caching
        file_path = f"{audio_dir}/{lesson_id}.mp3"
        chunk_count = 0
        
        # Stream chunks to client AND save to file simultaneously
        with open(file_path, "wb") as audio_file:
            for chunk in response:
                if chunk:
                    chunk_count += 1
                    audio_file.write(chunk)  # Cache for later use
                    yield chunk  # Stream to client immediately
        
        print(f"[TTS-Stream] Streaming complete: {chunk_count} chunks, saved to {file_path}")
        
    except Exception as error:
        print(f"[TTS-Stream] Error: {error}")
        # Yield empty to avoid breaking the stream
        return


async def generate_audio(text: str, lesson_id: str) -> Optional[Tuple[str, float]]:
    """
    Generate audio from text using Deepgram TTS. 
    Automatically chunks long text and creates sequential audio files.
    
    Returns:
        For single chunk: (url, duration)
        For multiple chunks: (playlist_json_url, total_duration)
        Returns None on error
    """
    
    # Get API key from settings
    api_key = settings.deepgram_api_key
    if not api_key:
        print("[TTS] No Deepgram API key found")
        return None
    
    # Check if text needs chunking
    max_chars = 1900  # Safe limit for Deepgram
    
    if len(text) > max_chars:
        print(f"[TTS] Text is {len(text)} chars, will chunk into segments")
        return await generate_audio_chunked(text, lesson_id, api_key)
    
    # Single chunk processing (original logic)
    try:
        print(f"[TTS] Generating audio for lesson {lesson_id}...")
        print(f"[TTS] Text length: {len(text)} characters")
        
        # Create Deepgram client
        deepgram = DeepgramClient(api_key=api_key)
        
        # Create directory if it doesn't exist
        audio_dir = "app/static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generate audio with Odysseus voice using correct v5.0.0 API
        response = deepgram.speak.v1.audio.generate(
            text=text,
            model="aura-2-odysseus-en"
        )
        
        # Save audio to file - response is a generator that yields bytes chunks
        file_path = f"{audio_dir}/{lesson_id}.mp3"
        with open(file_path, "wb") as audio_file:
            for chunk in response:
                audio_file.write(chunk)
        
        print(f"[TTS] Audio saved to {file_path}")
        
        # Get actual audio duration
        try:
            audio_file = MP3(file_path)
            duration = audio_file.info.length
            print(f"[TTS] Audio duration: {duration:.1f} seconds")
        except Exception as e:
            print(f"[TTS] Could not get audio duration: {e}")
            duration = 120.0  # Fallback duration
        
        # Return URL path and duration
        return (f"/static/audio/{lesson_id}.mp3", duration)
        
    except Exception as error:
        print(f"[TTS] Error: {error}")
        return None


async def generate_audio_chunked(text: str, lesson_id: str, api_key: str) -> Optional[Tuple[str, float]]:
    """
    Generate audio for long text by splitting into chunks and creating multiple audio files.
    
    Args:
        text: Full text to convert
        lesson_id: Base ID for lesson
        api_key: Deepgram API key
        
    Returns:
        Tuple of (playlist_metadata_url, total_duration) or None on error
    """
    try:
        # Split text into chunks
        chunks = chunk_text_by_sentences(text, max_chars=1900)
        
        if not chunks:
            print("[TTS-Chunked] No chunks generated")
            return None
        
        print(f"[TTS-Chunked] Generating {len(chunks)} audio chunks...")
        
        deepgram = DeepgramClient(api_key=api_key)
        audio_dir = "app/static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        
        chunk_metadata = []
        total_duration = 0.0
        pause_duration = 0.7  # 0.7 second pause between chunks
        
        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{lesson_id}_chunk_{i}"
            file_path = f"{audio_dir}/{chunk_id}.mp3"
            
            print(f"[TTS-Chunked] Generating chunk {i+1}/{len(chunks)} ({len(chunk_text)} chars)...")
            
            # Generate audio for this chunk
            response = deepgram.speak.v1.audio.generate(
                text=chunk_text,
                model="aura-2-odysseus-en"
            )
            
            # Save to file
            with open(file_path, "wb") as audio_file:
                for chunk_bytes in response:
                    audio_file.write(chunk_bytes)
            
            # Get duration
            try:
                audio_file = MP3(file_path)
                duration = audio_file.info.length
            except Exception as e:
                print(f"[TTS-Chunked] Could not get duration for chunk {i}: {e}")
                duration = 60.0  # Fallback
            
            chunk_metadata.append({
                "index": i,
                "file": f"/static/audio/{chunk_id}.mp3",
                "duration": duration,
                "start_time": total_duration,  # When this chunk starts in timeline
            })
            
            total_duration += duration
            
            # Add pause between chunks (except after last chunk)
            if i < len(chunks) - 1:
                total_duration += pause_duration
            
            print(f"[TTS-Chunked] Chunk {i+1} saved: {duration:.1f}s")
        
        # Save playlist metadata
        import json
        playlist_data = {
            "lesson_id": lesson_id,
            "total_duration": total_duration,
            "chunk_count": len(chunks),
            "pause_duration": pause_duration,
            "chunks": chunk_metadata
        }
        
        playlist_path = f"{audio_dir}/{lesson_id}_playlist.json"
        with open(playlist_path, "w") as f:
            json.dump(playlist_data, f, indent=2)
        
        print(f"[TTS-Chunked] ✅ Generated {len(chunks)} chunks, total duration: {total_duration:.1f}s")
        print(f"[TTS-Chunked] Playlist saved to {playlist_path}")
        
        # Return playlist URL instead of single audio URL
        return (f"/static/audio/{lesson_id}_playlist.json", total_duration)
        
    except Exception as error:
        print(f"[TTS-Chunked] Error: {error}")
        return None