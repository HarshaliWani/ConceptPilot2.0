"""View user proficiency from MongoDB."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "ConceptPilot"

async def view_proficiency():
    """View current proficiency for test user."""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    
    user = await users_collection.find_one({"_id": "user123"})
    
    if user:
        print("📊 User Proficiency Report")
        print("=" * 60)
        print(f"User ID: {user.get('_id', 'N/A')}")
        print(f"Username: {user.get('username', 'N/A')}")
        print(f"Email: {user.get('email', 'N/A')}")
        print("\n🎯 Topic Proficiency Scores:")
        print("=" * 60)
        proficiency = user.get("topic_proficiency", {})
        if proficiency:
            for topic, score in sorted(proficiency.items()):
                percentage = score * 100
                # Create visual bar
                bar_length = int(score * 50)
                bar = "█" * bar_length + "░" * (50 - bar_length)
                print(f"\n{topic}:")
                print(f"  Score: {score:.4f} ({percentage:.1f}%)")
                print(f"  [{bar}]")
        else:
            print("  ⚠️  No proficiency data yet")
        print("\n" + "=" * 60)
    else:
        print("❌ User not found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(view_proficiency())
