"""Create a test user in MongoDB."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "ConceptPilot"

async def create_test_user():
    """Create a test user for proficiency tracking."""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"_id": "user123"})
    
    if existing_user:
        print(f"✅ Test user already exists: user123")
        print(f"Current proficiency: {existing_user.get('topic_proficiency', {})}")
        return existing_user
    
    # Create test user
    user_doc = {
        "_id": "user123",  # Using string ID for simplicity
        "email": "test@conceptpilot.com",
        "username": "testuser",
        "full_name": "Test User",
        "topic_proficiency": {},  # Will be populated by quiz results
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await users_collection.insert_one(user_doc)
    print(f"✅ Created test user: user123")
    print(f"Email: {user_doc['email']}")
    
    client.close()
    return user_doc

async def view_user_proficiency():
    """View current proficiency for test user."""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    
    user = await users_collection.find_one({"_id": "user123"})
    
    if user:
        print("\n📊 User Proficiency Report")
        print("=" * 50)
        print(f"User: {user.get('username', 'N/A')}")
        print(f"Email: {user.get('email', 'N/A')}")
        print("\nTopic Proficiency:")
        proficiency = user.get("topic_proficiency", {})
        if proficiency:
            for topic, score in proficiency.items():
                percentage = score * 100
                print(f"  • {topic}: {score:.4f} ({percentage:.1f}%)")
        else:
            print("  No proficiency data yet")
        print("=" * 50)
    else:
        print("❌ User not found")
    
    client.close()

if __name__ == "__main__":
    print("Creating test user for proficiency tracking...\n")
    asyncio.run(create_test_user())
    print("\nViewing user proficiency...")
    asyncio.run(view_user_proficiency())
