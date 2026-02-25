"""Test script to verify streaming audio endpoint."""

import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"


async def test_streaming_endpoint():
    """Test the /audio/stream endpoint with a real lesson."""
    print("=" * 60)
    print("Testing Streaming Audio Endpoint")
    print("=" * 60)
    
    # Step 1: Generate a lesson first
    print("\n📝 Step 1: Generating a test lesson...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/lessons/generate",
            json={
                "topic": "Quantum Mechanics",
                "user_interest": "physics",
                "proficiency_level": "beginner",
                "grade_level": "high school"
            }
        )
    
    if response.status_code != 201:
        print(f"❌ Failed to create lesson: {response.status_code}")
        print(response.text)
        return
    
    lesson = response.json()
    lesson_id = lesson["_id"]
    print(f"✅ Lesson created: {lesson_id}")
    print(f"   Title: {lesson['title']}")
    
    # Step 2: Stream audio from the lesson
    print(f"\n🎵 Step 2: Streaming audio from lesson...")
    print(f"   Endpoint: GET {BASE_URL}/lessons/{lesson_id}/audio/stream")
    
    start_time = time.time()
    first_chunk_time = None
    chunk_count = 0
    total_bytes = 0
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "GET",
                f"{BASE_URL}/lessons/{lesson_id}/audio/stream"
            ) as stream_response:
                
                if stream_response.status_code != 200:
                    print(f"❌ Stream failed: {stream_response.status_code}")
                    error_text = await stream_response.aread()
                    print(f"   Error: {error_text.decode()}")
                    return
                
                print(f"✅ Stream started (Status: {stream_response.status_code})")
                print(f"   Content-Type: {stream_response.headers.get('content-type')}")
                print(f"\n📊 Receiving audio chunks...")
                
                async for chunk in stream_response.aiter_bytes(chunk_size=8192):
                    chunk_count += 1
                    total_bytes += len(chunk)
                    
                    # Record time of first chunk
                    if first_chunk_time is None:
                        first_chunk_time = time.time() - start_time
                        print(f"\n   🎉 FIRST CHUNK RECEIVED!")
                        print(f"   ⏱️  Time to first audio: {first_chunk_time:.2f}s")
                        print(f"   📦 Chunk size: {len(chunk)} bytes")
                        print(f"   ▶️  Frontend could START PLAYING NOW!")
                        print(f"\n   Streaming remaining chunks...\n")
                    
                    # Progress indicator
                    if chunk_count % 10 == 0:
                        elapsed = time.time() - start_time
                        kb_received = total_bytes / 1024
                        print(f"   [{elapsed:5.1f}s] Chunk #{chunk_count:3d} | {kb_received:6.1f}KB received")
        
        # Stream complete
        total_time = time.time() - start_time
        kb_total = total_bytes / 1024
        
        print(f"\n✅ Streaming complete!")
        print(f"\n📈 Statistics:")
        print(f"   Total chunks: {chunk_count}")
        print(f"   Total size: {kb_total:.1f}KB")
        print(f"   Total time: {total_time:.1f}s")
        print(f"   Time to first chunk: {first_chunk_time:.2f}s")
        print(f"   Average speed: {kb_total / total_time:.1f}KB/s")
        
        print(f"\n🎯 Performance Comparison:")
        print(f"   OLD (wait for full file): ~60s before playback")
        print(f"   NEW (streaming): {first_chunk_time:.2f}s before playback")
        print(f"   IMPROVEMENT: {60 / first_chunk_time:.1f}x faster! 🚀")
        
    except Exception as e:
        print(f"\n❌ Error during streaming: {e}")
        import traceback
        traceback.print_exc()


async def test_missing_lesson():
    """Test streaming with non-existent lesson ID."""
    print("\n" + "=" * 60)
    print("Testing Error Handling (Non-existent Lesson)")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/lessons/nonexistent123/audio/stream"
        )
    
    print(f"\nStatus: {response.status_code}")
    if response.status_code == 404:
        print("✅ Correctly returns 404 for missing lesson")
    else:
        print(f"⚠️  Expected 404, got {response.status_code}")


async def main():
    """Run all tests."""
    print("\n" + "🎵" * 30)
    print("STREAMING AUDIO ENDPOINT TEST SUITE")
    print("🎵" * 30 + "\n")
    
    print("⚠️  IMPORTANT: Make sure the FastAPI server is running!")
    print("   Run: uvicorn app.main:app --reload")
    print()
    
    input("Press Enter when server is ready... ")
    
    await test_streaming_endpoint()
    await test_missing_lesson()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
