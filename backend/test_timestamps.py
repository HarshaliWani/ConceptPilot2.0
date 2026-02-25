"""Test script to verify audio timestamp extraction with Groq Whisper."""

import asyncio
import os
from app.services.audio_timestamps import extract_word_timestamps, map_timestamps_to_board_actions

async def test_timestamp_extraction():
    """Test extracting word timestamps from an existing audio file."""
    print("=" * 60)
    print("Testing Audio Timestamp Extraction (Groq Whisper)")
    print("=" * 60)
    
    # Check for an existing audio file
    audio_dir = "app/static/audio"
    if not os.path.exists(audio_dir):
        print(f"\n❌ Audio directory not found: {audio_dir}")
        print("   Run a lesson generation first to create audio files.")
        return
    
    # Find the first audio file
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
    
    if not audio_files:
        print(f"\n❌ No audio files found in {audio_dir}")
        print("   Run test_streaming_tts.py first to generate a test audio file.")
        return
    
    # Use the most recent audio file
    audio_file = audio_files[-1]
    audio_path = os.path.join(audio_dir, audio_file)
    
    print(f"\n📁 Using audio file: {audio_file}")
    print(f"   Size: {os.path.getsize(audio_path) / 1024:.1f}KB")
    
    # Extract timestamps
    print(f"\n🎤 Calling Groq Whisper API for timestamp extraction...")
    timestamps = await extract_word_timestamps(audio_path)
    
    if timestamps is None:
        print("\n❌ Failed to extract timestamps")
        print("   Check that GROQ_API_KEY is set in your .env file")
        return
    
    if not timestamps:
        print("\n⚠️ No timestamps returned (empty list)")
        return
    
    # Display results
    print(f"\n✅ Successfully extracted {len(timestamps)} word timestamps!")
    print(f"\n📊 Sample timestamps (first 10 words):")
    print("-" * 60)
    
    for i, word_data in enumerate(timestamps[:10]):
        word = word_data['word']
        start = word_data['start']
        end = word_data['end']
        duration = end - start
        
        print(f"  [{start:6.2f}s - {end:6.2f}s] ({duration:4.2f}s) → '{word}'")
    
    if len(timestamps) > 10:
        print(f"  ... and {len(timestamps) - 10} more words")
    
    # Calculate statistics
    print(f"\n📈 Statistics:")
    print("-" * 60)
    total_duration = timestamps[-1]['end'] if timestamps else 0
    words_per_second = len(timestamps) / total_duration if total_duration > 0 else 0
    avg_word_duration = sum(w['end'] - w['start'] for w in timestamps) / len(timestamps)
    
    print(f"  Total words: {len(timestamps)}")
    print(f"  Total duration: {total_duration:.1f}s")
    print(f"  Words per second: {words_per_second:.2f}")
    print(f"  Avg word duration: {avg_word_duration:.3f}s")
    
    # Test syncing with mock board actions
    print(f"\n🎨 Testing timestamp-to-board-action mapping:")
    print("-" * 60)
    
    mock_board_actions = [
        {"timestamp": 0, "type": "text", "content": "Photosynthesis", "x": 300, "y": 50},
        {"timestamp": 5, "type": "circle", "content": "sunlight", "x": 200, "y": 150},
        {"timestamp": 10, "type": "text", "content": "energy", "x": 400, "y": 200},
    ]
    
    enhanced_actions = map_timestamps_to_board_actions(timestamps, mock_board_actions)
    
    for action in enhanced_actions:
        if 'original_timestamp' in action:
            print(f"  '{action['content']}': {action['original_timestamp']:.1f}s → {action['timestamp']:.1f}s (adjusted)")
        else:
            print(f"  (No content to sync)")
    
    print("\n" + "=" * 60)
    print("✅ Timestamp extraction test completed successfully!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Use timestamps in frontend for canvas synchronization")
    print("   2. Highlight words as they're spoken")
    print("   3. Adjust board action timing based on actual audio")

if __name__ == "__main__":
    asyncio.run(test_timestamp_extraction())
