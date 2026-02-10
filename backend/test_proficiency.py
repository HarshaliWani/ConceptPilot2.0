"""Test script for quiz proficiency tracking."""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def create_test_user():
    """Create a test user if it doesn't exist."""
    # For now, we'll use the test MongoDB script
    # In the future, add user creation endpoint
    print("Note: Using test user ID 'user123'")
    return "user123"

def generate_quiz(topic="Python Basics"):
    """Generate a quiz on the given topic."""
    url = f"{BASE_URL}/quizzes/generate"
    payload = {
        "topic": topic,
        "topic_description": f"Introduction to {topic}",
        "user_id": "user123"
    }
    
    print(f"\n📝 Generating quiz on '{topic}'...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Quiz created successfully!")
        print(f"Quiz ID: {data['_id']}")
        print(f"Questions: {len(data['questions'])}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None

def submit_quiz_perfect_score(quiz_data):
    """Submit quiz with all correct answers to test proficiency increase."""
    quiz_id = quiz_data["_id"]
    url = f"{BASE_URL}/quizzes/{quiz_id}/submit"
    
    # Generate perfect answers
    answers = {}
    for question in quiz_data["questions"]:
        answers[question["id"]] = question["correctAnswer"]
    
    payload = {
        "user_id": "user123",
        "quiz_id": quiz_id,
        "answers": answers,
        "time_taken_seconds": 300
    }
    
    print(f"\n📤 Submitting quiz with PERFECT score (all correct answers)...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Quiz submitted successfully!")
        print(f"Score: {data['score']:.1f}%")
        print(f"Correct: {data['correct_count']}/{data['total_questions']}")
        print(f"Passed: {data['passed']}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None

def submit_quiz_poor_score(quiz_data):
    """Submit quiz with all wrong answers to test proficiency decrease."""
    quiz_id = quiz_data["_id"]
    url = f"{BASE_URL}/quizzes/{quiz_id}/submit"
    
    # Generate all wrong answers
    answers = {}
    for question in quiz_data["questions"]:
        correct = question["correctAnswer"]
        # Pick any wrong answer
        wrong_answer = (correct + 1) % len(question["options"])
        answers[question["id"]] = wrong_answer
    
    payload = {
        "user_id": "user123",
        "quiz_id": quiz_id,
        "answers": answers,
        "time_taken_seconds": 200
    }
    
    print(f"\n📤 Submitting quiz with POOR score (all wrong answers)...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Quiz submitted successfully!")
        print(f"Score: {data['score']:.1f}%")
        print(f"Correct: {data['correct_count']}/{data['total_questions']}")
        print(f"Passed: {data['passed']}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None

def submit_quiz_mixed_score(quiz_data):
    """Submit quiz with difficult questions correct, easy ones wrong."""
    quiz_id = quiz_data["_id"]
    url = f"{BASE_URL}/quizzes/{quiz_id}/submit"
    
    # Answer hard questions correctly, easy questions wrong
    answers = {}
    for question in quiz_data["questions"]:
        difficulty = question.get("difficulty", "medium").lower()
        if difficulty == "hard":
            # Correct answer for hard questions
            answers[question["id"]] = question["correctAnswer"]
        else:
            # Wrong answer for easy/medium questions
            correct = question["correctAnswer"]
            wrong_answer = (correct + 1) % len(question["options"])
            answers[question["id"]] = wrong_answer
    
    payload = {
        "user_id": "user123",
        "quiz_id": quiz_id,
        "answers": answers,
        "time_taken_seconds": 400
    }
    
    print(f"\n📤 Submitting quiz with MIXED score (hard correct, easy/medium wrong)...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Quiz submitted successfully!")
        print(f"Score: {data['score']:.1f}%")
        print(f"Correct: {data['correct_count']}/{data['total_questions']}")
        print(f"Passed: {data['passed']}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None

def main():
    print("=" * 60)
    print("QUIZ PROFICIENCY TRACKING TEST")
    print("=" * 60)
    
    # Create test user
    user_id = create_test_user()
    
    # Test 1: Perfect score
    print("\n" + "=" * 60)
    print("TEST 1: Perfect Score (All Correct)")
    print("=" * 60)
    quiz1 = generate_quiz("Python Basics")
    if quiz1:
        submit_quiz_perfect_score(quiz1)
    
    # Test 2: Poor score
    print("\n" + "=" * 60)
    print("TEST 2: Poor Score (All Wrong)")
    print("=" * 60)
    quiz2 = generate_quiz("JavaScript Fundamentals")
    if quiz2:
        submit_quiz_poor_score(quiz2)
    
    # Test 3: Mixed score (demonstrates difficulty weighting)
    print("\n" + "=" * 60)
    print("TEST 3: Mixed Score (Hard Correct, Easy Wrong)")
    print("=" * 60)
    quiz3 = generate_quiz("Data Structures")
    if quiz3:
        submit_quiz_mixed_score(quiz3)
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print("\n💡 Check backend logs for proficiency updates")
    print("Format: '[QuizSubmit] Updated proficiency for user...'\n")

if __name__ == "__main__":
    main()
