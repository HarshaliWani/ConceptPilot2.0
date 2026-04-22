# Narration Script Migration Guide

## Overview

This migration script cleans up the `narration_script` field in MongoDB lessons collection. Sometimes the entire LLM response JSON is stored instead of just the narration text.

## Issues Handled

1. **JSON stored as string**: Full LLM response stored as JSON string instead of extracted narration
2. **Malformed data types**: narration_script stored as dict, object, or other non-string types
3. **Incomplete extractions**: Partial JSON with embedded narration
4. **Edge cases**: Various malformed formats

## Setup

### Prerequisites
- Python 3.8+
- Motor (async MongoDB driver) - included in `requirements.txt`
- Running MongoDB instance

### Installation
The script uses existing dependencies from `requirements.txt`. No additional packages needed.

## Usage

### 1. **Dry Run (Recommended First)**
Preview what would be changed without making any changes:

```bash
cd backend
python migrate_narration_script.py --mongodb-uri mongodb://localhost:27017
```

### 2. **Apply Migration**
After reviewing dry run results, apply the migration:

```bash
python migrate_narration_script.py --mongodb-uri mongodb://localhost:27017 --apply
```

### 3. **With Custom Database**
If using a different database name:

```bash
python migrate_narration_script.py --mongodb-uri mongodb://localhost:27017 --database CustomDB --apply
```

### 4. **Batch Size Configuration**
Adjust batch processing size (default: 100):

```bash
python migrate_narration_script.py --apply --batch-size 50
```

### 5. **Full Example on Windows**
```powershell
cd backend
& '.\\.venv\\Scripts\\Activate.ps1'
python migrate_narration_script.py --mongodb-uri mongodb://localhost:27017 --apply
```

## Output Example

```
2026-04-22 10:15:30,123 - INFO - ✓ Connected to MongoDB: ConceptPilot
2026-04-22 10:15:30,456 - INFO - Total lessons to process: 45

2026-04-22 10:15:31,200 - INFO - Processing batch 1 (skip=0, limit=100)...

2026-04-22 10:15:31,250 - INFO - Lesson 507f1f77bcf86cd799439011:
2026-04-22 10:15:31,250 - INFO -   Current type: str
2026-04-22 10:15:31,250 - INFO -   Current length: 2847
2026-04-22 10:15:31,250 - INFO -   Status: JSON extracted
2026-04-22 10:15:31,250 - INFO -   New length: 342
2026-04-22 10:15:31,250 - INFO -   ✓ Updated in database

...

============================================================
MIGRATION SUMMARY
============================================================
Total lessons processed: 45
Already clean: 38
Malformed found: 3
Extracted from JSON: 4
Fallback extraction used: 0
Errors: 0
Updated in database: 4
============================================================
```

## What Gets Updated

For each migrated lesson, the following fields are modified:

```json
{
  "narration_script": "cleaned narration text only",
  "migrated_at": "2026-04-22T10:15:31.000Z",
  "migration_status": "cleaned"
}
```

## Verification

### Check Migration Results
```javascript
// In MongoDB Compass or shell

// Count cleaned lessons
db.lessons.countDocuments({ migration_status: "cleaned" })

// View a cleaned lesson
db.lessons.findOne({ migration_status: "cleaned" })

// See which ones still have issues (are still JSON)
db.lessons.find({ 
  narration_script: { $regex: "^{" } 
})

// Statistics
db.lessons.aggregate([
  { $group: {
      _id: "$migration_status",
      count: { $sum: 1 }
    }
  }
])
```

### Quick Check Script
```python
# Quick verification after migration
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def verify():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ConceptPilot"]
    
    # Find narrations that are still JSON
    bad_narrations = await db.lessons.count_documents({
        "narration_script": { "$regex": "^{" }
    })
    
    print(f"Lessons with JSON narrations: {bad_narrations}")
    
    # Find cleaned narrations
    cleaned = await db.lessons.count_documents({
        "migration_status": "cleaned"
    })
    
    print(f"Cleaned lessons: {cleaned}")
    
    client.close()

asyncio.run(verify())
```

## Rollback (If Needed)

The migration adds `migrated_at` and `migration_status` fields but doesn't backup the original. To rollback:

1. **From backup**: Restore MongoDB from backup before migration
2. **Manual restore**: If you need to revert specific documents, check your MongoDB backup/recovery options

**Recommendation**: Always backup MongoDB before running the migration script.

## Troubleshooting

### Script runs but doesn't find MongoDB
```
✗ Failed to connect to MongoDB: [connection error]
```
**Solution**: Ensure MongoDB is running and URI is correct
```bash
# Check MongoDB is running
mongod --version
# Verify connection string
python migrate_narration_script.py --mongodb-uri mongodb://localhost:27017
```

### Permission errors updating documents
```
✗ Failed to update
```
**Solution**: Ensure MongoDB user has write permissions to the database

### Script hangs or times out
**Solution**: Reduce batch size
```bash
python migrate_narration_script.py --apply --batch-size 25
```

## Performance

- **Processing speed**: ~100-200 lessons per minute
- **Memory usage**: Minimal (batch processing)
- **Database load**: Low
- **Estimated time for 1000 lessons**: 5-10 minutes

## Safety Features

1. **Dry run mode**: Default behavior doesn't modify database
2. **Batch processing**: Processes in batches to avoid memory issues
3. **Validation**: Checks if narration is already clean before updating
4. **Logging**: Detailed logs show what changed and why
5. **Error handling**: Continues processing even if individual documents fail

## Scheduled Maintenance

To prevent this issue in the future, review [app/services/lesson_generator.py](../app/services/lesson_generator.py) to ensure narration_script extraction is working correctly in the generation logic.

See [IMPLEMENTATION_COMPLETE.md](../IMPLEMENTATION_COMPLETE.md) for related lesson generation details.
