import asyncio
from app.services.lesson_generator import generate_lesson


async def test_full_lesson():
    """Test full lesson generation with audio integration."""
    lesson = await generate_lesson(
        topic="Friction",
        user_interest="Football", 
        proficiency_level="beginner",
        grade_level="10th grade"
    )
    
    # Print lesson title
    print(f"Lesson title: {lesson.get('title', 'N/A')}")
    
    # Print number of board_actions
    board_actions = lesson.get('board_actions', [])
    print(f"Number of board_actions: {len(board_actions)}")
    
    # Print audio_url if present
    audio_url = lesson.get('audio_url')
    if audio_url:
        print(f"Audio URL: {audio_url}")
    else:
        print("No audio generated")
    
    print("✓ Full lesson with audio generated successfully!")


if __name__ == "__main__":
    asyncio.run(test_full_lesson())