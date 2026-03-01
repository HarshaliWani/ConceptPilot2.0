#!/usr/bin/env python3
"""
Quick Lesson Validation Utility
===============================

Test individual lesson generation and validation for debugging and quick checks.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from evaluation_framework import LessonValidator, generate_lesson_with_metrics, PerformanceMetrics


async def test_single_lesson(topic: str = "Quadratic Equations", 
                           user_interest: str = "video games",
                           proficiency: str = "beginner",
                           grade: str = "high school"):
    """Test a single lesson generation and validation."""
    
    print(f"🧪 Testing Single Lesson Generation")
    print(f"   Topic: {topic}")
    print(f"   Interest: {user_interest}")
    print(f"   Level: {proficiency} ({grade})")
    print()
    
    validator = LessonValidator()
    metrics = PerformanceMetrics()
    
    print("⏳ Generating lesson...")
    
    lesson, validation = await generate_lesson_with_metrics(
        topic=topic,
        user_interest=user_interest,
        proficiency=proficiency,
        grade=grade,
        validator=validator,
        metrics=metrics
    )
    
    if validation["success"]:
        print("✅ Lesson generated successfully!")
        print(f"   Generation Time: {validation['generation_time']:.2f}s")
        print(f"   Overall Score: {validation['overall_score']:.1f}/100")
        print()
        
        print("📊 Validation Breakdown:")
        print(f"   Structure Score: {validation['structure']['structure_score']:.1f}/100")
        print(f"   Visual Diversity: {validation['board_actions']['visual_diversity_score']:.1f}/100")
        print(f"   Educational Quality: {validation['narration']['educational_quality_score']:.1f}/100")
        print()
        
        print("📝 Lesson Content:")
        print(f"   Title: {lesson.get('title', 'N/A')}")
        print(f"   Duration: {lesson.get('duration', 'N/A')} seconds")
        print(f"   Board Actions: {len(lesson.get('board_actions', []))} actions")
        print(f"   Narration Length: {len(lesson.get('narration_script', '').split())} words")
        
        if lesson.get('audio_url'):
            print(f"   Audio: {lesson['audio_url']}")
            
        print()
        
        # Show sample narration (first 200 chars)
        narration = lesson.get('narration_script', '')
        if narration:
            print("📢 Sample Narration:")
            print(f"   \"{narration[:200]}{'...' if len(narration) > 200 else ''}\"")
        
        # Show sample board actions
        board_actions = lesson.get('board_actions', [])
        if board_actions:
            print(f"\n🎨 Sample Board Actions (first 3):")
            for i, action in enumerate(board_actions[:3]):
                print(f"   {i+1}. [{action.get('timestamp', 0):.1f}s] {action.get('type', 'unknown')}")
                if action.get('content'):
                    print(f"      Content: \"{action['content'][:50]}{'...' if len(str(action['content'])) > 50 else ''}\"")
        
        # Save detailed result
        result_data = {
            "test_timestamp": datetime.utcnow().isoformat(),
            "parameters": {
                "topic": topic,
                "user_interest": user_interest,
                "proficiency": proficiency,
                "grade": grade
            },
            "lesson": lesson,
            "validation": validation
        }
        
        filename = f"test_lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n💾 Detailed result saved to: {filename}")
        
    else:
        print("❌ Lesson generation failed!")
        print(f"   Error: {validation.get('error', 'Unknown error')}")
        print(f"   Duration: {validation['generation_time']:.2f}s")


async def run_mini_evaluation(num_lessons: int = 5):
    """Run a small batch evaluation for testing."""
    
    print(f"🧪 Running Mini-Evaluation ({num_lessons} lessons)")
    print("=" * 40)
    
    # Quick topic list
    mini_topics = [
        "Quadratic Equations", 
        "Newton's Laws", 
        "Ohm's Law", 
        "Probability", 
        "Electromagnetic Induction"
    ][:num_lessons]
    
    validator = LessonValidator()
    metrics = PerformanceMetrics()
    
    results = []
    
    for i, topic in enumerate(mini_topics):
        print(f"⏳ Generating lesson {i+1}/{num_lessons}: {topic}")
        
        lesson, validation = await generate_lesson_with_metrics(
            topic=topic,
            user_interest="technology",
            proficiency="intermediate",
            grade="high school",
            validator=validator,
            metrics=metrics
        )
        
        results.append({
            "topic": topic,
            "success": validation["success"],
            "score": validation["overall_score"],
            "time": validation["generation_time"]
        })
        
        status = "✅" if validation["success"] else "❌"
        score = f"{validation['overall_score']:.1f}/100" if validation["success"] else "N/A"
        print(f"   {status} Score: {score} ({validation['generation_time']:.1f}s)")
    
    print("\n📊 Mini-Evaluation Summary:")
    successes = sum(1 for r in results if r["success"])
    print(f"   Success Rate: {successes}/{num_lessons} ({successes/num_lessons*100:.1f}%)")
    
    if successes > 0:
        avg_score = sum(r["score"] for r in results if r["success"]) / successes
        avg_time = sum(r["time"] for r in results if r["success"]) / successes
        print(f"   Average Score: {avg_score:.1f}/100")
        print(f"   Average Time: {avg_time:.2f}s")
    
    return results


def main():
    """Main CLI interface."""
    
    if len(sys.argv) < 2:
        print("🔧 LESSON VALIDATION UTILITY")
        print("=" * 30)
        print("Usage:")
        print("  python validate_lessons.py single [topic]")
        print("  python validate_lessons.py mini [count]")
        print()
        print("Examples:")
        print("  python validate_lessons.py single \"Calculus Derivatives\"")
        print("  python validate_lessons.py mini 3")
        return
    
    command = sys.argv[1].lower()
    
    if command == "single":
        topic = sys.argv[2] if len(sys.argv) > 2 else "Quadratic Equations"
        asyncio.run(test_single_lesson(topic=topic))
        
    elif command == "mini":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        asyncio.run(run_mini_evaluation(num_lessons=count))
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: single, mini")


if __name__ == "__main__":
    main()