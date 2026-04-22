# Narration Script Migration Tools - Complete Index

## Overview

This package includes tools to identify and fix corrupted `narration_script` fields in MongoDB where the entire LLM response JSON is stored instead of just the narration text.

## Quick Start (30 seconds)

### Windows CMD
```cmd
cd backend
verify_narration.bat
```

### Windows PowerShell
```powershell
cd backend
.\verify_narration.ps1
```

### Linux/Mac/Git Bash
```bash
cd backend
python verify_narration_script.py
```

## Files Included

### 1. **Verification Tools** (No database changes)
- `verify_narration_script.py` - Python script (main tool)
- `verify_narration.bat` - Windows batch wrapper
- `verify_narration.ps1` - Windows PowerShell wrapper

**Purpose**: Scan your database to see how many lessons have narration_script issues.

**Use when**: You want to check the current state before migrating

### 2. **Migration Tools** (Makes database changes)
- `migrate_narration_script.py` - Python script (main tool)
- `migrate_narration.bat` - Windows batch wrapper
- `migrate_narration.ps1` - Windows PowerShell wrapper

**Purpose**: Clean up corrupted narration_script fields

**Use when**: You're ready to fix the issues (after verifying with tools above)

### 3. **Documentation**
- `MIGRATION_README.md` - Quick reference guide
- `MIGRATION_NARRATION_SCRIPT.md` - Detailed documentation
- `NARRATION_MIGRATION_INDEX.md` - This file

## Typical Workflow

```
1. Verify current state
   ↓
2. Review verification report
   ↓
3. Backup MongoDB (important!)
   ↓
4. Preview migration (dry run)
   ↓
5. Apply migration
   ↓
6. Verify results
```

## Step-by-Step Guide

### Step 1: Verify Current Database State

**Windows (Command Prompt):**
```cmd
cd backend
verify_narration.bat
```

**Windows (PowerShell):**
```powershell
cd backend
.\verify_narration.ps1
```

**Linux/Mac:**
```bash
cd backend
python verify_narration_script.py
```

**Expected output:**
```
Total lessons analyzed: 45

Data Quality Breakdown:
  ✓ Valid strings: 38 (84.4%)
  ✗ JSON strings: 4 (8.9%)
  ✗ Non-strings: 1 (2.2%)
  ✗ Too short: 2 (4.4%)

⚠ Found 7 lessons with issues
```

### Step 2: Backup MongoDB

**Using mongodump:**
```bash
mongodump --uri mongodb://localhost:27017 --db ConceptPilot --out ./backup
```

### Step 3: Preview Migration (Dry Run)

**Windows (Command Prompt):**
```cmd
cd backend
migrate_narration.bat
```

**Windows (PowerShell):**
```powershell
cd backend
.\migrate_narration.ps1
```

**Linux/Mac:**
```bash
cd backend
python migrate_narration_script.py
```

This shows what will be changed WITHOUT making any changes to your database.

### Step 4: Apply Migration

**Windows (Command Prompt):**
```cmd
cd backend
migrate_narration.bat --apply
```

**Windows (PowerShell):**
```powershell
cd backend
.\migrate_narration.ps1 --apply
```

**Linux/Mac:**
```bash
cd backend
python migrate_narration_script.py --apply
```

### Step 5: Verify Results

Run verification again to confirm all issues are fixed:

```cmd
verify_narration.bat
```

Should show all lessons as valid strings!

## Advanced Usage

### Custom MongoDB URI
```cmd
verify_narration.bat --mongodb-uri mongodb+srv://user:password@cluster.mongodb.net
migrate_narration.bat --apply --mongodb-uri mongodb+srv://user:password@cluster.mongodb.net
```

### Custom Database Name
```cmd
verify_narration.bat --database MyDatabase
migrate_narration.bat --apply --database MyDatabase
```

### Adjust Batch Size (for large databases)
```cmd
migrate_narration.bat --apply --batch-size 50
```

### Combine Options
```cmd
migrate_narration.bat --apply --mongodb-uri mongodb://localhost:27017 --database ConceptPilot --batch-size 100
```

## Understanding Narration Script Issues

### The Problem

**WRONG** - Stores entire LLM response as JSON string in narration_script:
```json
{
  "_id": ObjectId("..."),
  "narration_script": "{\"topic\":\"Physics\",\"title\":\"F=ma\",\"narration_script\":\"...\",\"board_actions\":[...]}"
}
```

**CORRECT** - Stores only the narration text:
```json
{
  "_id": ObjectId("..."),
  "narration_script": "Today we'll learn about Newton's second law. Force equals mass times acceleration..."
}
```

### Where It Comes From

The issue occurs in [app/services/lesson_generator.py](../app/services/lesson_generator.py) when:
1. LLM returns JSON response
2. Response is sometimes stored as-is instead of extracting just the `narration_script` field
3. Database ends up with JSON strings instead of plain text

### Impact

- **Frontend**: May fail to display narration properly
- **TTS**: May try to convert JSON to audio instead of just narration
- **Audio**: May generate incorrect or missing audio
- **Timestamps**: May fail to sync properly

## What the Migration Does

For each lesson with issues:

1. **Detects** if narration_script is corrupted (JSON, dict, malformed)
2. **Extracts** just the narration text from the JSON
3. **Updates** the document with clean narration only
4. **Records** migration metadata:
   - `migrated_at`: When the migration ran
   - `migration_status`: "cleaned"

### Example of Changes

**Before:**
```json
{
  "narration_script": "{\"topic\":\"Photosynthesis\",\"narration_script\":\"Plants use sunlight...\",\"duration\":180}"
}
```

**After:**
```json
{
  "narration_script": "Plants use sunlight to create energy...",
  "migrated_at": ISODate("2026-04-22T10:15:31Z"),
  "migration_status": "cleaned"
}
```

## Safety Features

✅ **Dry run mode** - Default behavior doesn't modify database  
✅ **Batch processing** - Processes in batches for memory efficiency  
✅ **Validation** - Checks if already clean before updating  
✅ **Detailed logging** - Shows exactly what's being changed  
✅ **Error handling** - Continues if individual documents fail  
✅ **Idempotent** - Safe to run multiple times  

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | MongoDB not running. Start MongoDB first |
| "Virtual environment not found" | Run scripts from `backend` directory |
| Script hangs | Stop with Ctrl+C, try with `--batch-size 50` |
| Permission denied | Check MongoDB user has write access |
| No changes after migration | Lessons may already be clean; that's OK! |

## Performance

- **Speed**: 100-200 lessons per minute
- **Memory**: Low (batch processing)
- **Database load**: Minimal
- **Time for 1000 lessons**: ~5-10 minutes

## Monitoring Migration

### Check Progress in Real-Time
```bash
# In a separate terminal, monitor database changes
mongo ConceptPilot
db.lessons.countDocuments({ migration_status: "cleaned" })
```

### View Migration Details
```bash
# See lessons that were migrated
db.lessons.find({ migration_status: "cleaned" }).limit(5)

# Check migration timestamps
db.lessons.aggregate([
  { $match: { migration_status: "cleaned" } },
  { $group: { 
      _id: null, 
      count: { $sum: 1 }, 
      earliest: { $min: "$migrated_at" },
      latest: { $max: "$migrated_at" }
    }
  }
])
```

## Rollback

If migration causes issues:

### Option 1: From MongoDB Backup
```bash
mongorestore --uri mongodb://localhost:27017 ./backup
```

### Option 2: Manual Query (Remove migration fields)
```javascript
// Remove migration metadata (but keeps the cleaned narration)
db.lessons.updateMany(
  { migration_status: "cleaned" },
  { $unset: { migration_status: "", migrated_at: "" } }
)
```

## Getting Help

1. **Before starting**: Read [MIGRATION_README.md](MIGRATION_README.md)
2. **Detailed info**: See [MIGRATION_NARRATION_SCRIPT.md](MIGRATION_NARRATION_SCRIPT.md)
3. **Questions**: Check the MongoDB schema in [MONGODB_SCHEMA.md](../MONGODB_SCHEMA.md)
4. **Code issues**: Review [app/services/lesson_generator.py](../app/services/lesson_generator.py)

## Maintenance

To prevent this issue in future:

1. **Review** lesson generation logic for proper field extraction
2. **Test** LLM response parsing thoroughly
3. **Monitor** narration_script in new lessons
4. **Add** validation in API endpoints to catch malformed data

See [app/api/v1/endpoints/lessons.py](../app/api/v1/endpoints/lessons.py) for the save logic.

## Summary of Tools

| Tool | Purpose | Changes DB | When to Use |
|------|---------|------------|------------|
| `verify_narration_script.py` | Check status | No | Before migrating |
| `verify_narration.bat/.ps1` | Windows wrapper for verify | No | Windows users |
| `migrate_narration_script.py` | Fix issues | Yes | After verifying |
| `migrate_narration.bat/.ps1` | Windows wrapper for migrate | Yes | Windows users |

---

**Created**: April 22, 2026  
**Database**: ConceptPilot  
**Collection**: lessons  
**Field**: narration_script
