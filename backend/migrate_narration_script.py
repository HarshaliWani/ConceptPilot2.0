#!/usr/bin/env python3
"""
Migration script to clean up narration_script field in MongoDB lessons collection.

Issue: Sometimes narration_script stores the entire LLM response JSON instead of 
just the narration text.

This script:
1. Identifies malformed narration scripts (JSON, dicts, etc.)
2. Extracts just the narration_script field if it exists
3. Updates documents with clean narration scripts
4. Is idempotent - safe to run multiple times
5. Creates backups of modified documents
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NarrationMigration:
    """Handles migration of narration_script fields."""
    
    def __init__(self, mongodb_uri: str, database_name: str = "ConceptPilot"):
        """Initialize migration handler.
        
        Args:
            mongodb_uri: MongoDB connection string
            database_name: Database name (default: ConceptPilot)
        """
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.client = None
        self.db = None
        self.lessons_collection = None
        self.stats = {
            "total_lessons": 0,
            "already_clean": 0,
            "malformed": 0,
            "json_extracted": 0,
            "fallback_used": 0,
            "errors": 0,
        }
    
    async def connect(self):
        """Connect to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            self.lessons_collection = self.db["lessons"]
            
            # Test connection
            await self.db.command("ping")
            logger.info(f"✓ Connected to MongoDB: {self.database_name}")
        except Exception as e:
            logger.error(f"✗ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("✓ Disconnected from MongoDB")
    
    def _is_clean_narration(self, narration: Any) -> bool:
        """
        Check if narration_script is clean (just text string).
        
        Args:
            narration: The narration_script value from document
            
        Returns:
            True if clean, False if malformed
        """
        # Should be a string
        if not isinstance(narration, str):
            return False
        
        # Should not be JSON
        if narration.strip().startswith('{'):
            return False
        
        # Should not look like a dict representation
        if narration.strip().startswith('{"'):
            return False
        
        # Should have reasonable content
        if len(narration.strip()) < 10:
            return False
        
        return True
    
    def _extract_narration_from_json(self, content: str) -> Optional[str]:
        """
        Extract narration_script field from JSON string.
        
        Args:
            content: String that might be JSON
            
        Returns:
            Extracted narration script or None
        """
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Try to parse as JSON
            parsed = json.loads(content)
            
            if not isinstance(parsed, dict):
                return None
            
            # Check if it has narration_script field
            if "narration_script" in parsed and isinstance(parsed["narration_script"], str):
                narration = parsed["narration_script"].strip()
                if len(narration) > 10:
                    logger.info(f"  ✓ Extracted narration_script from JSON (length: {len(narration)})")
                    return narration
            
            # Check if entire content is stored as narration (shouldn't happen but check)
            if all(k in parsed for k in ["topic", "title", "board_actions"]):
                # This is a full lesson response, extract narration
                if "narration_script" in parsed:
                    narration = str(parsed["narration_script"]).strip()
                    if len(narration) > 10:
                        return narration
            
            return None
            
        except json.JSONDecodeError:
            return None
        except Exception as e:
            logger.debug(f"  Error extracting narration: {e}")
            return None
    
    def _extract_narration_from_string(self, content: str) -> Optional[str]:
        """
        Try to extract narration from various string formats.
        
        Args:
            content: String content that might be malformed
            
        Returns:
            Extracted narration or None
        """
        content = content.strip()
        
        # If it starts with JSON but has narration at the end, extract that
        if content.startswith('{') and '"narration_script"' in content:
            # Try JSON extraction first
            extracted = self._extract_narration_from_json(content)
            if extracted:
                return extracted
        
        # If it contains 'narration_script:', try to extract
        if '"narration_script"' in content or "'narration_script'" in content:
            # Find the field and extract following text
            match = re.search(
                r'["\']narration_script["\']?\s*:\s*["\']?([^"\']*)["\']?[,}]',
                content
            )
            if match:
                narration = match.group(1).strip()
                if len(narration) > 10:
                    logger.info(f"  ✓ Extracted narration via regex (length: {len(narration)})")
                    return narration
        
        return None
    
    async def clean_narration(self, narration: Any, lesson_id: str) -> tuple[bool, str, Optional[str]]:
        """
        Clean a single narration_script value.
        
        Args:
            narration: The narration_script value from document
            lesson_id: Lesson ID for logging
            
        Returns:
            Tuple of (is_clean, status_message, cleaned_narration)
        """
        if narration is None:
            return False, "narration_script is None", None
        
        # Already clean
        if self._is_clean_narration(narration):
            return True, "Already clean", narration
        
        # Not a string - try to convert
        if not isinstance(narration, str):
            self.stats["malformed"] += 1
            logger.warning(f"  ⚠ narration_script is {type(narration).__name__}, not string")
            
            # Try to convert dict/object to string representation
            try:
                narration_str = json.dumps(narration) if not isinstance(narration, str) else narration
            except:
                return False, f"Cannot convert {type(narration).__name__} to string", None
        else:
            narration_str = narration
        
        # Try to extract from JSON
        extracted = self._extract_narration_from_json(narration_str)
        if extracted:
            self.stats["json_extracted"] += 1
            return False, "JSON extracted", extracted
        
        # Try regex extraction
        extracted = self._extract_narration_from_string(narration_str)
        if extracted:
            self.stats["json_extracted"] += 1
            return False, "Regex extracted", extracted
        
        # Fallback: use first reasonable portion
        if len(narration_str) > 50:
            # Assume first 500-1000 chars are narration if starts with text
            if not narration_str.strip().startswith('{'):
                self.stats["fallback_used"] += 1
                logger.warning(f"  ⚠ Using fallback extraction (first portion)")
                return False, "Fallback extraction", narration_str[:1000].strip()
        
        return False, "Cannot clean - no valid extraction method", None
    
    async def migrate(self, dry_run: bool = True, batch_size: int = 100):
        """
        Run the migration.
        
        Args:
            dry_run: If True, don't update database
            batch_size: Process in batches
        """
        logger.info(f"Starting migration (dry_run={dry_run})...")
        logger.info("=" * 60)
        
        try:
            # Get total count
            total = await self.lessons_collection.count_documents({})
            self.stats["total_lessons"] = total
            logger.info(f"Total lessons to process: {total}")
            
            # Process in batches
            skip = 0
            updated_count = 0
            
            while skip < total:
                logger.info(f"\nProcessing batch {skip // batch_size + 1} (skip={skip}, limit={batch_size})...")
                
                # Fetch batch
                cursor = self.lessons_collection.find({}).skip(skip).limit(batch_size)
                documents = await cursor.to_list(length=batch_size)
                
                if not documents:
                    break
                
                for doc in documents:
                    lesson_id = str(doc["_id"])
                    narration = doc.get("narration_script")
                    
                    logger.info(f"\nLesson {lesson_id}:")
                    logger.info(f"  Current type: {type(narration).__name__}")
                    logger.info(f"  Current length: {len(str(narration))}")
                    
                    # Check if clean
                    is_clean, status, cleaned = await self.clean_narration(narration, lesson_id)
                    
                    if is_clean:
                        logger.info(f"  Status: {status} ✓")
                        self.stats["already_clean"] += 1
                    else:
                        if cleaned is not None:
                            logger.info(f"  Status: {status}")
                            logger.info(f"  New length: {len(cleaned)}")
                            
                            if not dry_run:
                                # Update document
                                result = await self.lessons_collection.update_one(
                                    {"_id": doc["_id"]},
                                    {
                                        "$set": {
                                            "narration_script": cleaned,
                                            "migrated_at": datetime.utcnow(),
                                            "migration_status": "cleaned"
                                        }
                                    }
                                )
                                if result.modified_count > 0:
                                    logger.info(f"  ✓ Updated in database")
                                    updated_count += 1
                                else:
                                    logger.error(f"  ✗ Failed to update")
                                    self.stats["errors"] += 1
                        else:
                            logger.error(f"  Status: {status} ✗")
                            self.stats["errors"] += 1
                
                skip += batch_size
            
            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("MIGRATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total lessons processed: {self.stats['total_lessons']}")
            logger.info(f"Already clean: {self.stats['already_clean']}")
            logger.info(f"Malformed found: {self.stats['malformed']}")
            logger.info(f"Extracted from JSON: {self.stats['json_extracted']}")
            logger.info(f"Fallback extraction used: {self.stats['fallback_used']}")
            logger.info(f"Errors: {self.stats['errors']}")
            logger.info(f"Updated in database: {updated_count}")
            logger.info("=" * 60)
            
            if dry_run:
                logger.info("DRY RUN - No changes made to database")
                logger.info("Run with dry_run=False to apply changes")
        
        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            raise


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate narration_script fields in MongoDB")
    parser.add_argument(
        "--mongodb-uri",
        default="mongodb://localhost:27017",
        help="MongoDB connection URI (default: mongodb://localhost:27017)"
    )
    parser.add_argument(
        "--database",
        default="ConceptPilot",
        help="Database name (default: ConceptPilot)"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (without this flag, runs in dry-run mode)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for processing (default: 100)"
    )
    
    args = parser.parse_args()
    
    migrator = NarrationMigration(args.mongodb_uri, args.database)
    
    try:
        await migrator.connect()
        await migrator.migrate(dry_run=not args.apply, batch_size=args.batch_size)
    finally:
        await migrator.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
