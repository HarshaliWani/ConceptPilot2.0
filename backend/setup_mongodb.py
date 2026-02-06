"""MongoDB collections and indexes setup script."""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings


async def setup_mongodb():
    """Create collections and indexes in MongoDB."""
    settings = get_settings()
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    print(f"🔄 Setting up MongoDB database: {settings.mongodb_db_name}")
    print(f"📍 Connection: {settings.mongodb_url}\n")
    
    try:
        # Ping to verify connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB\n")
        
        # Create users collection
        print("📝 Setting up 'users' collection...")
        if "users" not in await db.list_collection_names():
            await db.create_collection("users")
            print("   ✅ Created 'users' collection")
        else:
            print("   ℹ️  'users' collection already exists")
        
        # Create indexes for users
        await db.users.create_index("email", unique=True)
        print("   ✅ Created unique index on 'email'")
        
        await db.users.create_index("username", unique=True)
        print("   ✅ Created unique index on 'username'")
        
        # Create lessons collection
        print("\n📝 Setting up 'lessons' collection...")
        if "lessons" not in await db.list_collection_names():
            await db.create_collection("lessons")
            print("   ✅ Created 'lessons' collection")
        else:
            print("   ℹ️  'lessons' collection already exists")
        
        # Create indexes for lessons
        await db.lessons.create_index("topic")
        print("   ✅ Created index on 'topic'")
        
        await db.lessons.create_index("tailored_to_interest")
        print("   ✅ Created index on 'tailored_to_interest'")
        
        await db.lessons.create_index([("created_at", -1)])
        print("   ✅ Created index on 'created_at' (descending)")
        
        # Create text index for full-text search
        await db.lessons.create_index([
            ("topic", "text"),
            ("title", "text"),
            ("narration_script", "text")
        ])
        print("   ✅ Created text index for full-text search")
        
        # Create user_progress collection
        print("\n📝 Setting up 'user_progress' collection...")
        if "user_progress" not in await db.list_collection_names():
            await db.create_collection("user_progress")
            print("   ✅ Created 'user_progress' collection")
        else:
            print("   ℹ️  'user_progress' collection already exists")
        
        # Create indexes for user_progress
        await db.user_progress.create_index(
            [("user_id", 1), ("lesson_id", 1)],
            unique=True
        )
        print("   ✅ Created unique compound index on 'user_id' and 'lesson_id'")
        
        await db.user_progress.create_index([
            ("user_id", 1),
            ("last_accessed", -1)
        ])
        print("   ✅ Created compound index on 'user_id' and 'last_accessed'")
        
        await db.user_progress.create_index([
            ("lesson_id", 1),
            ("status", 1)
        ])
        print("   ✅ Created compound index on 'lesson_id' and 'status'")
        
        # Display collection info
        print("\n📊 Database Summary:")
        collections = await db.list_collection_names()
        print(f"   Database: {settings.mongodb_db_name}")
        print(f"   Collections: {', '.join(collections)}\n")
        
        # Display index information
        print("📑 Indexes Created:")
        for collection_name in ["users", "lessons", "user_progress"]:
            if collection_name in collections:
                collection = db[collection_name]
                indexes = await collection.list_indexes().to_list(length=None)
                print(f"\n   {collection_name.upper()}:")
                for idx in indexes:
                    print(f"      • {idx['name']}: {idx['key']}")
        
        print("\n✅ MongoDB setup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error setting up MongoDB: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    print("🚀 ConceptPilot MongoDB Setup\n")
    asyncio.run(setup_mongodb())
