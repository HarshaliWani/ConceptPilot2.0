#!/usr/bin/env python3
"""
Verification script to check narration_script data quality in MongoDB.

This script helps identify issues with narration_script storage without making changes.
Run this before and after migration to verify results.
"""

import asyncio
import json
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NarrationVerifier:
    """Verify narration_script data quality."""
    
    def __init__(self, mongodb_uri: str, database_name: str = "ConceptPilot"):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            await self.db.command("ping")
            logger.info(f"✓ Connected to MongoDB: {self.database_name}")
        except Exception as e:
            logger.error(f"✗ Failed to connect: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
    
    async def verify(self):
        """Run verification checks."""
        logger.info("Starting verification...\n")
        
        total = await self.db.lessons.count_documents({})
        logger.info(f"Total lessons: {total}\n")
        
        stats = {
            "total": total,
            "valid_strings": 0,
            "json_strings": 0,
            "non_strings": 0,
            "null_or_missing": 0,
            "too_short": 0,
            "cleaned_status": 0,
            "samples": []
        }
        
        logger.info("=" * 70)
        logger.info("NARRATION_SCRIPT DATA TYPE ANALYSIS")
        logger.info("=" * 70)
        
        cursor = self.db.lessons.find({}).limit(1000)
        
        async for doc in cursor:
            narration = doc.get("narration_script")
            lesson_id = str(doc["_id"])
            
            # Check if cleaned
            if doc.get("migration_status") == "cleaned":
                stats["cleaned_status"] += 1
            
            # Categorize
            if narration is None:
                stats["null_or_missing"] += 1
                stats["samples"].append({
                    "id": lesson_id,
                    "status": "NULL/MISSING",
                    "type": "null",
                    "length": 0
                })
            
            elif not isinstance(narration, str):
                stats["non_strings"] += 1
                narration_type = type(narration).__name__
                logger.warning(f"  ⚠ {lesson_id}: {narration_type}")
                stats["samples"].append({
                    "id": lesson_id,
                    "status": f"NOT_STRING ({narration_type})",
                    "type": narration_type,
                    "length": len(str(narration))
                })
            
            elif len(narration.strip()) < 10:
                stats["too_short"] += 1
                stats["samples"].append({
                    "id": lesson_id,
                    "status": "TOO_SHORT",
                    "type": "string",
                    "length": len(narration)
                })
            
            elif narration.strip().startswith('{'):
                stats["json_strings"] += 1
                logger.warning(f"  ⚠ {lesson_id}: Stored as JSON (length: {len(narration)})")
                
                # Try to parse and see what's inside
                try:
                    parsed = json.loads(narration)
                    if isinstance(parsed, dict) and "narration_script" in parsed:
                        inner_narration = parsed["narration_script"]
                        logger.info(f"     └─ Contains 'narration_script' field (length: {len(str(inner_narration))})")
                except:
                    logger.info(f"     └─ Invalid JSON")
                
                stats["samples"].append({
                    "id": lesson_id,
                    "status": "JSON_STORED",
                    "type": "json_string",
                    "length": len(narration)
                })
            
            else:
                stats["valid_strings"] += 1
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("VERIFICATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total lessons analyzed: {stats['total']}")
        logger.info(f"\nData Quality Breakdown:")
        logger.info(f"  ✓ Valid strings: {stats['valid_strings']} ({stats['valid_strings']/max(stats['total'], 1)*100:.1f}%)")
        logger.info(f"  ✗ JSON strings: {stats['json_strings']} ({stats['json_strings']/max(stats['total'], 1)*100:.1f}%)")
        logger.info(f"  ✗ Non-strings: {stats['non_strings']} ({stats['non_strings']/max(stats['total'], 1)*100:.1f}%)")
        logger.info(f"  ✗ Too short: {stats['too_short']} ({stats['too_short']/max(stats['total'], 1)*100:.1f}%)")
        logger.info(f"  ✗ Null/Missing: {stats['null_or_missing']} ({stats['null_or_missing']/max(stats['total'], 1)*100:.1f}%)")
        logger.info(f"\nMigration Status:")
        logger.info(f"  Already cleaned: {stats['cleaned_status']}")
        
        issues_count = (stats['json_strings'] + stats['non_strings'] + 
                       stats['too_short'] + stats['null_or_missing'])
        
        logger.info(f"\n{'='*70}")
        if issues_count == 0:
            logger.info("✓ All narration scripts are valid! No migration needed.")
        else:
            logger.info(f"⚠ Found {issues_count} lessons with issues")
            logger.info("\nRun migration to fix:")
            logger.info("  python migrate_narration_script.py --mongodb-uri <uri> --apply")
        logger.info("=" * 70)
        
        return stats


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify narration_script data quality")
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
    
    args = parser.parse_args()
    
    verifier = NarrationVerifier(args.mongodb_uri, args.database)
    
    try:
        await verifier.connect()
        await verifier.verify()
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return 1
    finally:
        await verifier.disconnect()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
