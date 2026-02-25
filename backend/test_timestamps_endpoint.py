"""Test script to verify the word timestamps endpoint."""

import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"


async def test_timestamps_endpoint():
    """Test the /timestamps endpoint with a real lesson."""
    print("=" * 70)
    print("Testing Word Timestamps Endpoint (Groq Whisper)")
    print("=" * 70)
    
    # Step 1: Generate a lesson
    print("\n📝 Step 1: Generating a test lesson...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/lessons/generate",
            json={
                "topic": "Cellular Respiration",
                "user_interest": "biology",
                "proficiency_level": "intermediate",
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
    print(f"   Audio URL: {lesson.get('audio_url', 'No audio yet')}")
    print(f"   Duration: {lesson.get('duration', 0):.1f}s")
    
    # Step 2: Extract word timestamps
    print(f"\n🎤 Step 2: Extracting word timestamps with Groq Whisper...")
    print(f"   Endpoint: GET {BASE_URL}/lessons/{lesson_id}/timestamps")
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(
                f"{BASE_URL}/lessons/{lesson_id}/timestamps"
            )
        
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            return
        
        data = response.json()
        
        print(f"\n✅ Timestamps extracted in {elapsed:.1f}s!")
        print(f"\n📊 Response Summary:")
        print("-" * 70)
        print(f"   Lesson ID: {data['lesson_id']}")
        print(f"   Audio URL: {data['audio_url']}")
        print(f"   Duration: {data['duration']:.1f}s")
        print(f"   Word Count: {data['word_count']}")
        print(f"   Message: {data.get('message', '')}")
        
        # Display sample timestamps
        word_timestamps = data['word_timestamps']
        print(f"\n📝 Sample Word Timestamps (first 15 words):")
        print("-" * 70)
        
        for i, word_data in enumerate(word_timestamps[:15]):
            word = word_data['word']
            start = word_data['start']
            end = word_data['end']
            duration = end - start
            
            # Add visual timeline
            timeline_pos = int((start / data['duration']) * 50)
            timeline = "." * timeline_pos + "█" + "." * (50 - timeline_pos)
            
            print(f"   {i+1:2d}. [{start:6.2f}s - {end:6.2f}s] ({duration:4.2f}s) → '{word}'")
            if i % 5 == 4:  # Show timeline every 5 words
                print(f"       {timeline}")
        
        if len(word_timestamps) > 15:
            print(f"   ... and {len(word_timestamps) - 15} more words")
        
        # Calculate statistics
        print(f"\n📈 Statistics:")
        print("-" * 70)
        words_per_second = data['word_count'] / data['duration']
        avg_word_duration = sum(
            w['end'] - w['start'] for w in word_timestamps
        ) / len(word_timestamps)
        
        print(f"   Total words: {data['word_count']}")
        print(f"   Total duration: {data['duration']:.1f}s")
        print(f"   Words per second: {words_per_second:.2f}")
        print(f"   Avg word duration: {avg_word_duration:.3f}s")
        print(f"   Speech rate: {'Normal' if 2 <= words_per_second <= 3 else 'Fast' if words_per_second > 3 else 'Slow'}")
        
        # Show synced board actions
        synced_actions = data.get('board_actions_synced', [])
        if synced_actions:
            print(f"\n🎨 Board Actions Synchronized:")
            print("-" * 70)
            
            adjusted_count = sum(1 for action in synced_actions if 'original_timestamp' in action)
            print(f"   Total board actions: {len(synced_actions)}")
            print(f"   Actions adjusted: {adjusted_count}")
            
            # Show first few adjusted actions
            adjusted_actions = [a for a in synced_actions if 'original_timestamp' in a][:5]
            if adjusted_actions:
                print(f"\n   Sample timing adjustments:")
                for action in adjusted_actions:
                    content = action.get('content', action.get('type', 'Unknown'))
                    orig = action['original_timestamp']
                    new = action['timestamp']
                    diff = new - orig
                    symbol = "→" if diff > 0 else "←"
                    print(f"      '{content}': {orig:.1f}s {symbol} {new:.1f}s (Δ {abs(diff):.1f}s)")
        
        # Demonstrate frontend usage
        print(f"\n💡 Frontend Integration Example:")
        print("-" * 70)
        print("""
        // Fetch timestamps
        const data = await fetch(`/api/v1/lessons/${lessonId}/timestamps`)
            .then(r => r.json());
        
        // Sync canvas with audio
        audioElement.addEventListener('timeupdate', () => {
            const currentTime = audioElement.currentTime;
            const currentWord = data.word_timestamps.find(
                w => w.start <= currentTime && w.end >= currentTime
            );
            
            if (currentWord) {
                // Highlight current word
                highlightWord(currentWord.word);
                
                // Trigger board actions at exact timing
                data.board_actions_synced.forEach(action => {
                    if (action.timestamp === Math.floor(currentTime)) {
                        drawOnCanvas(action);
                    }
                });
            }
        });
        """)
        
        print("\n" + "=" * 70)
        print("✅ Timestamps endpoint test completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_error_cases():
    """Test error handling."""
    print("\n" + "=" * 70)
    print("Testing Error Handling")
    print("=" * 70)
    
    # Test 1: Non-existent lesson
    print("\n🧪 Test 1: Non-existent lesson")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/lessons/nonexistent123/timestamps"
        )
    print(f"   Status: {response.status_code}")
    print(f"   ✅ Correctly returns 404" if response.status_code == 404 else f"   ⚠️  Expected 404")
    
    # Test 2: Lesson without audio (would need a lesson without audio, skip for now)
    print("\n🧪 Test 2: Lesson without audio")
    print("   ⏭️  Skipped (requires lesson without audio)")


async def main():
    """Run all tests."""
    print("\n" + "🎵" * 35)
    print("WORD TIMESTAMPS ENDPOINT TEST SUITE")
    print("🎵" * 35 + "\n")
    
    print("⚠️  IMPORTANT: Make sure the FastAPI server is running!")
    print("   Run: uvicorn app.main:app --reload")
    print()
    
    input("Press Enter when server is ready... ")
    
    await test_timestamps_endpoint()
    await test_error_cases()
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    print("\n💡 Next steps:")
    print("   1. Update frontend to use word timestamps")
    print("   2. Implement canvas-audio synchronization")
    print("   3. Add word highlighting as audio plays")
    print("   4. Use synced board actions for perfect timing")


if __name__ == "__main__":
    asyncio.run(main())
