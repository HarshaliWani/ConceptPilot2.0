"""Test quiz generation endpoint."""
import asyncio
import httpx


async def test_quiz_generation():
    """Test quiz generation endpoint."""
    base_url = "http://localhost:8000/api/v1"
    
    # Test payload
    payload = {
        "topic": "Python Basics",
        "topic_description": "Basic concepts in Python programming including variables, data types, and functions"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("Testing quiz generation endpoint...")
            print(f"Payload: {payload}")
            
            response = await client.post(
                f"{base_url}/quizzes/generate",
                json=payload,
                timeout=60.0
            )
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print(f"\n✓ Quiz generated successfully!")
                print(f"Quiz ID: {data.get('_id')}")
                print(f"Topic: {data.get('topic')}")
                print(f"Number of questions: {len(data.get('questions', []))}")
                print(f"\nSample Question:")
                if data.get('questions'):
                    q = data['questions'][0]
                    print(f"  Q: {q['question']}")
                    print(f"  Options: {q['options']}")
                    print(f"  Difficulty: {q['difficulty']}")
                return data
            else:
                print(f"\n✗ Error: {response.text}")
                return None
                
        except httpx.ConnectError:
            print("\n✗ Error: Could not connect to server. Is the backend running?")
            return None
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return None


if __name__ == "__main__":
    asyncio.run(test_quiz_generation())
