"""MongoDB CRUD operations helper."""

from typing import Any, Dict, List, Optional, TypeVar
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class MongoDBOperations:
    """Generic MongoDB CRUD operations."""

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        """Initialize MongoDB operations for a specific collection.
        
        Args:
            db: AsyncIOMotorDatabase instance from Motor
            collection_name: Name of the collection
        """
        self.collection: AsyncIOMotorCollection = db[collection_name]

    async def create(self, document: Dict[str, Any]) -> str:
        """Create a new document.
        
        Args:
            document: Dictionary containing document data
            
        Returns:
            Inserted document ID as string
        """
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def read_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Read a document by ID.
        
        Args:
            doc_id: Document ID as string
            
        Returns:
            Document or None if not found
        """
        try:
            object_id = ObjectId(doc_id)
            return await self.collection.find_one({"_id": object_id})
        except Exception:
            return None

    async def read_many(
        self,
        query: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "_id",
        sort_order: int = -1,
    ) -> List[Dict[str, Any]]:
        """Read multiple documents.
        
        Args:
            query: MongoDB query filter
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort_by: Field to sort by
            sort_order: Sort order (1 for ascending, -1 for descending)
            
        Returns:
            List of documents
        """
        if query is None:
            query = {}
        
        cursor = self.collection.find(query)
        cursor = cursor.sort(sort_by, sort_order)
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def update(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a document.
        
        Args:
            doc_id: Document ID as string
            update_data: Dictionary containing fields to update
            
        Returns:
            True if document was updated, False otherwise
        """
        try:
            object_id = ObjectId(doc_id)
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def delete(self, doc_id: str) -> bool:
        """Delete a document.
        
        Args:
            doc_id: Document ID as string
            
        Returns:
            True if document was deleted, False otherwise
        """
        try:
            object_id = ObjectId(doc_id)
            result = await self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception:
            return False

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document by query.
        
        Args:
            query: MongoDB query filter
            
        Returns:
            Document or None if not found
        """
        return await self.collection.find_one(query)

    async def find_many(
        self,
        query: Dict[str, Any],
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Find multiple documents by query.
        
        Args:
            query: MongoDB query filter
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
        """
        cursor = self.collection.find(query).limit(limit)
        return await cursor.to_list(length=limit)

    async def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents.
        
        Args:
            query: MongoDB query filter
            
        Returns:
            Number of documents matching query
        """
        if query is None:
            query = {}
        return await self.collection.count_documents(query)

    async def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete multiple documents.
        
        Args:
            query: MongoDB query filter
            
        Returns:
            Number of deleted documents
        """
        result = await self.collection.delete_many(query)
        return result.deleted_count

    async def create_index(self, fields: str | List[tuple], **kwargs) -> str:
        """Create an index on the collection.
        
        Args:
            fields: Field name(s) for the index
            **kwargs: Additional index options
            
        Returns:
            Index name
        """
        return await self.collection.create_index(fields, **kwargs)

    async def create_text_index(self, fields: List[str]) -> str:
        """Create a text index for full-text search.
        
        Args:
            fields: List of field names for text search
            
        Returns:
            Index name
        """
        index_spec = [(field, "text") for field in fields]
        return await self.collection.create_index(index_spec)

    async def text_search(self, search_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform full-text search.
        
        Args:
            search_text: Search text
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        cursor = self.collection.find(
            {"$text": {"$search": search_text}}
        ).limit(limit)
        return await cursor.to_list(length=limit)
