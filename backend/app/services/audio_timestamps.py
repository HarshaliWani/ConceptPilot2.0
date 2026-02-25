"""Audio timestamp extraction service using Groq Whisper API."""

import os
from typing import List, Dict, Optional
from groq import Groq
from app.core.config import get_settings

settings = get_settings()


async def extract_word_timestamps(audio_file_path: str) -> Optional[List[Dict]]:
    """
    Extract word-level timestamps from audio file using Groq Whisper.
    
    This enables perfect synchronization between audio playback and canvas animations.
    Groq's Whisper API is FREE and returns precise word-level timestamps.
    
    Args:
        audio_file_path: Path to the audio file (e.g., "app/static/audio/lesson123.mp3")
        
    Returns:
        List of word timestamp dictionaries:
        [
            {"word": "photosynthesis", "start": 0.5, "end": 1.2},
            {"word": "is", "start": 1.3, "end": 1.4},
            {"word": "the", "start": 1.5, "end": 1.7},
            ...
        ]
        
    Example usage:
        timestamps = await extract_word_timestamps("app/static/audio/lesson123.mp3")
        # Use timestamps to sync canvas animations with audio
        for timestamp in timestamps:
            if current_time >= timestamp['start'] and current_time <= timestamp['end']:
                highlight_word(timestamp['word'])
    """
    
    groq_api_key = settings.groq_api_key
    if not groq_api_key:
        print("[Timestamps] No Groq API key found")
        return None
    
    # Check if audio file exists
    if not os.path.exists(audio_file_path):
        print(f"[Timestamps] Audio file not found: {audio_file_path}")
        return None
    
    try:
        print(f"[Timestamps] Processing audio file: {audio_file_path}")
        print(f"[Timestamps] File size: {os.path.getsize(audio_file_path) / 1024:.1f}KB")
        
        # Initialize Groq client
        client = Groq(api_key=groq_api_key)
        
        # Open and read audio file
        with open(audio_file_path, "rb") as audio_file:
            # Use Whisper with verbose_json for detailed timestamps
            print("[Timestamps] Calling Groq Whisper API...")
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_file_path), audio_file.read()),
                model="whisper-large-v3-turbo",  # Fast and accurate
                response_format="verbose_json",  # Required for timestamps
                timestamp_granularities=["word"]  # Word-level precision
            )
        
        # Extract word timestamps from response
        word_timestamps = []
        
        # Debug: Check response structure
        print(f"[Timestamps] Response type: {type(transcription)}")
        
        # Handle different response formats (dict or object)
        if hasattr(transcription, 'words'):
            words_data = transcription.words
        elif isinstance(transcription, dict) and 'words' in transcription:
            words_data = transcription['words']
        else:
            print(f"[Timestamps] ⚠️ Unexpected response structure: {transcription}")
            return []
        
        if words_data:
            for word_data in words_data:
                # Handle both dict and object formats
                if isinstance(word_data, dict):
                    word = word_data.get('word', '').strip()
                    start = float(word_data.get('start', 0))
                    end = float(word_data.get('end', 0))
                else:
                    word = word_data.word.strip()
                    start = float(word_data.start)
                    end = float(word_data.end)
                
                word_timestamps.append({
                    "word": word,
                    "start": start,
                    "end": end
                })
            
            print(f"[Timestamps] ✅ Extracted {len(word_timestamps)} word timestamps")
            print(f"[Timestamps] First word: '{word_timestamps[0]['word']}' at {word_timestamps[0]['start']:.2f}s")
            print(f"[Timestamps] Last word: '{word_timestamps[-1]['word']}' at {word_timestamps[-1]['end']:.2f}s")
            print(f"[Timestamps] Total duration: {word_timestamps[-1]['end']:.1f}s")
            
            return word_timestamps
        else:
            print("[Timestamps] ⚠️ No words found in transcription")
            return []
        
    except Exception as error:
        print(f"[Timestamps] ❌ Error: {error}")
        return None


def map_timestamps_to_board_actions(
    word_timestamps: List[Dict],
    board_actions: List[Dict]
) -> List[Dict]:
    """
    Map word timestamps to board actions for precise synchronization.
    
    This intelligent mapping ensures board actions appear exactly when
    the corresponding words are spoken in the narration.
    
    Args:
        word_timestamps: List of word timestamps from extract_word_timestamps()
        board_actions: List of board actions from lesson generator
        
    Returns:
        Enhanced board actions with adjusted timestamps based on actual audio timing
        
    Example:
        # Board action says "draw circle at 5s"
        # But the word "circle" is actually spoken at 6.2s in the audio
        # This function adjusts the board action to appear at 6.2s for perfect sync
    """
    
    if not word_timestamps or not board_actions:
        return board_actions
    
    print(f"[Sync] Mapping {len(word_timestamps)} words to {len(board_actions)} board actions")
    
    # Helper function to normalize text for matching
    def normalize_text(text):
        """Remove punctuation and extra spaces, convert to lowercase."""
        import re
        text = re.sub(r'[^\w\s]', '', text.lower())
        return ' '.join(text.split())
    
    # Create word lookup with normalized keys
    word_lookup = {}
    for word_data in word_timestamps:
        normalized = normalize_text(word_data['word'])
        if normalized:
            word_lookup[normalized] = word_data
    
    # Create full transcript for multi-word matching
    full_transcript = ' '.join([normalize_text(w['word']) for w in word_timestamps])
    
    enhanced_actions = []
    synced_count = 0
    unsynced_count = 0
    
    for action in board_actions:
        enhanced_action = action.copy()
        matched = False
        
        # Skip clear actions - they don't need syncing
        if action.get('type') == 'clear':
            enhanced_action['_synced'] = 'skip'
            enhanced_actions.append(enhanced_action)
            continue
        
        # Try to find when action content/label is spoken
        # Check both 'content' (for text actions) and 'label' (for shape actions)
        text_to_match = None
        if 'content' in action and action['content']:
            text_to_match = action['content']
        elif 'label' in action and action['label']:
            text_to_match = action['label']
        
        if text_to_match:
            search_text = normalize_text(text_to_match)
            
            # Strategy 1: Look for multi-word phrase in transcript
            if search_text in full_transcript:
                # Find which word this phrase starts at
                words_list = [normalize_text(w['word']) for w in word_timestamps]
                search_words = search_text.split()
                
                for i in range(len(words_list) - len(search_words) + 1):
                    phrase = ' '.join(words_list[i:i+len(search_words)])
                    if phrase == search_text:
                        # Sync to the start of this phrase
                        original_timestamp = action.get('timestamp', 0)
                        new_timestamp = word_timestamps[i]['start']
                        enhanced_action['timestamp'] = new_timestamp
                        enhanced_action['original_timestamp'] = original_timestamp
                        enhanced_action['_synced'] = True
                        matched = True
                        synced_count += 1
                        print(f"[Sync] ✓ '{text_to_match[:30]}...': {original_timestamp:.1f}s → {new_timestamp:.1f}s")
                        break
            
            # Strategy 2: Single word lookup
            if not matched and search_text in word_lookup:
                original_timestamp = action.get('timestamp', 0)
                new_timestamp = word_lookup[search_text]['start']
                enhanced_action['timestamp'] = new_timestamp
                enhanced_action['original_timestamp'] = original_timestamp
                enhanced_action['_synced'] = True
                matched = True
                synced_count += 1
                print(f"[Sync] ✓ '{text_to_match[:30]}...': {original_timestamp:.1f}s → {new_timestamp:.1f}s")
            
            # Strategy 3: Partial word match (first word of multi-word content)
            if not matched and ' ' in search_text:
                first_word = search_text.split()[0]
                if first_word in word_lookup:
                    original_timestamp = action.get('timestamp', 0)
                    new_timestamp = word_lookup[first_word]['start']
                    enhanced_action['timestamp'] = new_timestamp
                    enhanced_action['original_timestamp'] = original_timestamp
                    enhanced_action['_synced'] = 'partial'
                    matched = True
                    synced_count += 1
                    print(f"[Sync] ≈ '{text_to_match[:30]}...' (partial): {original_timestamp:.1f}s → {new_timestamp:.1f}s")
        
        # If still not matched, keep original timestamp but mark as unsynced
        if not matched:
            enhanced_action['_synced'] = False
            unsynced_count += 1
            if text_to_match:
                print(f"[Sync] ✗ '{text_to_match[:30]}...' - no match found, keeping original timestamp {action.get('timestamp', 0):.1f}s")
        
        enhanced_actions.append(enhanced_action)
    
    # Calculate stats (excluding skipped actions)
    total_syncable = len([a for a in enhanced_actions if a.get('_synced') != 'skip'])
    
    print(f"[Sync] ✅ Synced: {synced_count}/{total_syncable} actions ({100*synced_count//total_syncable if total_syncable > 0 else 0}%)")
    print(f"[Sync] ⚠️  Un-synced: {unsynced_count}/{total_syncable} actions")
    
    return enhanced_actions


def get_timestamp_at_position(word_timestamps: List[Dict], text_position: int) -> Optional[float]:
    """
    Get audio timestamp for a specific character position in the transcribed text.
    
    Useful for syncing arbitrary points in the narration with audio timing.
    
    Args:
        word_timestamps: List of word timestamps
        text_position: Character position in the full transcribed text
        
    Returns:
        Audio timestamp (seconds) at that text position, or None
    """
    
    if not word_timestamps:
        return None
    
    # Reconstruct full text with positions
    current_pos = 0
    for word_data in word_timestamps:
        word_length = len(word_data['word'])
        if current_pos <= text_position <= current_pos + word_length:
            return word_data['start']
        current_pos += word_length + 1  # +1 for space
    
    return None
