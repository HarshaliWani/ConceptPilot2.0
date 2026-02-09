"""Text-to-speech service using Deepgram API."""

import os
import asyncio
from typing import Optional, Tuple
from deepgram import DeepgramClient
from app.core.config import get_settings
from mutagen.mp3 import MP3

settings = get_settings()


async def generate_audio(text: str, lesson_id: str) -> Optional[Tuple[str, float]]:
    """Generate audio from text using Deepgram TTS. Returns (url, duration) or None."""
    
    # Get API key from settings
    api_key = settings.deepgram_api_key
    if not api_key:
        print("[TTS] No Deepgram API key found")
        return None
    
    # Truncate text to Deepgram's 2000 character limit
    max_chars = 1950  # Leave some buffer
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
        print(f"[TTS] Text truncated to {max_chars} characters for Deepgram limit")
    
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