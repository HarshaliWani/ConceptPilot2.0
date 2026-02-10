"""Test script to generate a lesson."""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def generate_lesson():
    """Generate a test lesson."""
    url = f"{BASE_URL}/lessons/generate"
    payload = {
        "topic": "Python Basics",
        "user_interest": "web development",
        "proficiency_level": "beginner"
    }
    
    print(f"Generating lesson...")
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Lesson created successfully!")
        print(f"Lesson ID: {data['_id']}")
        print(f"Title: {data['title']}")
        print(f"Topic: {data['topic']}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None

def list_lessons():
    """List all lessons."""
    url = f"{BASE_URL}/lessons/"
    
    print(f"\nFetching lessons...")
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        lessons = response.json()
        print(f"✅ Found {len(lessons)} lessons:")
        for lesson in lessons:
            print(f"  - ID: {lesson['_id']}")
            print(f"    Title: {lesson['title']}")
            print(f"    Topic: {lesson['topic']}")
            print()
        return lessons
    else:
        print(f"❌ Error: {response.text}")
        return []

if __name__ == "__main__":
    # Generate a lesson
    lesson = generate_lesson()
    
    # List all lessons
    lessons = list_lessons()
