import asyncio
from app.services.tts_service import generate_audio


async def test_tts():
    """Test TTS service in isolation."""
    result = await generate_audio("Friction is the force that opposes motion between two surfaces in contact.", "test_lesson")
    
    print(result)
    
    if result is not None:
        print(f"✓ Audio generated successfully: {result}")
    else:
        print("✗ Audio generation failed")


if __name__ == "__main__":
    asyncio.run(test_tts())