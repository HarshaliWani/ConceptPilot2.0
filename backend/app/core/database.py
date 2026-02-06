"""MongoDB database connection and management."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import get_settings


class MongoDB:
    """MongoDB connection manager using Motor (async driver)."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls) -> None:
        """Create database connection."""
        settings = get_settings()
        # Use the Motor async client
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        cls.db = cls.client[settings.mongodb_db_name]
        
        # Verify connection by listing databases
        try:
            await cls.client.admin.command('ping')
            print(f"✅ Connected to MongoDB at {settings.mongodb_url}")
            print(f"📦 Using database: {settings.mongodb_db_name}")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls) -> None:
        """Close database connection."""
        if cls.client is not None:
            cls.client.close()
            print("✅ Disconnected from MongoDB")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None:
            raise RuntimeError("Database connection not established. Call connect_db() first.")
        return cls.db

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Get MongoDB client instance."""
        if cls.client is None:
            raise RuntimeError("Database connection not established. Call connect_db() first.")
        return cls.client


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency for FastAPI to get database instance."""
    return MongoDB.get_db()
