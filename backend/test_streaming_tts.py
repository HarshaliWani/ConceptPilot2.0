"""Test script to verify streaming TTS functionality."""

import asyncio
from app.services.tts_service import generate_audio_stream

async def test_streaming():
    """Test the streaming audio generation."""
    print("=" * 60)
    print("Testing Streaming TTS")
    print("=" * 60)
    
    test_text = """
    Today we'll explore photosynthesis, the amazing process that plants use 
    to convert sunlight into energy. This fundamental biological process is 
    crucial for life on Earth.
    """
    
    lesson_id = "test_streaming_lesson"
    chunk_count = 0
    total_bytes = 0
    
    print(f"\n📝 Text to synthesize: {test_text[:100]}...")
    print(f"\n🎤 Starting streaming audio generation...\n")
    
    async for chunk in generate_audio_stream(test_text.strip(), lesson_id):
        chunk_count += 1
        total_bytes += len(chunk)
        
        # Show progress
        if chunk_count == 1:
            print(f"✅ First chunk received! ({len(chunk)} bytes)")
            print("   → Frontend could start playing audio NOW!")
        elif chunk_count % 10 == 0:
            print(f"   Chunk #{chunk_count}: {len(chunk)} bytes (total: {total_bytes/1024:.1f}KB)")
    
    print(f"\n✅ Streaming complete!")
    print(f"   Total chunks: {chunk_count}")
    print(f"   Total size: {total_bytes/1024:.1f}KB")
    print(f"   Audio saved to: app/static/audio/{lesson_id}.mp3")
    print("\n" + "=" * 60)
    print("Streaming TTS test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_streaming())
