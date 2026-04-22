# Narration Script Migration Tools

Quick reference for cleaning up `narration_script` field in MongoDB.

## Problem

Sometimes the `narration_script` field stores the entire LLM response JSON instead of just the spoken narration text.

**Example of Problem:**
```json
// WRONG - stores entire JSON response
{
  "_id": ObjectId("..."),
  "narration_script": "{\"topic\": \"...\", \"title\": \"...\", \"narration_script\": \"...\", \"board_actions\": [...]}"
}

// CORRECT - stores only narration text
{
  "_id": ObjectId("..."),
  "narration_script": "Today we'll learn about... The process starts when..."
}
```

## Tools

### 1. **verify_narration_script.py** - Check Status
Scan your database to see how many lessons have issues (no changes made).

```bash
# Quick check
python verify_narration_script.py

# With custom MongoDB URI
python verify_narration_script.py --mongodb-uri mongodb://user:pass@host:27017
```

**Output tells you:**
- How many valid narration scripts exist
- How many are stored as JSON strings
- How many are malformed or missing
- Whether migration is needed

### 2. **migrate_narration_script.py** - Fix Issues
Clean up the narration scripts (can make changes to database).

```bash
# Preview changes (recommended first)
python migrate_narration_script.py

# Apply changes
python migrate_narration_script.py --apply

# With custom database
python migrate_narration_script.py --mongodb-uri mongodb://localhost:27017 --apply
```

## Quick Start

### Step 1: Check Your Database
```bash
python verify_narration_script.py
```

Output example:
```
Total lessons analyzed: 45

Data Quality Breakdown:
  ✓ Valid strings: 38 (84.4%)
  ✗ JSON strings: 4 (8.9%)
  ✗ Non-strings: 1 (2.2%)
  ✗ Too short: 2 (4.4%)

⚠ Found 7 lessons with issues
```

### Step 2: Preview Migration (Dry Run)
```bash
python migrate_narration_script.py
```

This shows you what will be changed without actually changing anything.

### Step 3: Apply Migration
```bash
python migrate_narration_script.py --apply
```

### Step 4: Verify Results
```bash
python verify_narration_script.py
```

Should now show all valid strings!

## Windows PowerShell Example

```powershell
cd backend

# Activate venv
& '.\.venv\Scripts\Activate.ps1'

# Verify status
python verify_narration_script.py

# Preview migration
python migrate_narration_script.py

# Apply changes
python migrate_narration_script.py --apply

# Verify again
python verify_narration_script.py
```

## MongoDB Connection

### Local MongoDB
```bash
python verify_narration_script.py --mongodb-uri mongodb://localhost:27017
python migrate_narration_script.py --apply --mongodb-uri mongodb://localhost:27017
```

### MongoDB Atlas (Cloud)
```bash
python verify_narration_script.py --mongodb-uri mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### Custom Database Name
```bash
python verify_narration_script.py --database CustomDB
python migrate_narration_script.py --apply --database CustomDB
```

## What Gets Updated

For each migrated lesson:
- `narration_script`: Cleaned to contain only the narration text
- `migrated_at`: Timestamp when the migration ran
- `migration_status`: Set to "cleaned"

## Backup First!

**Always backup your MongoDB before running migration:**

```bash
# Backup (with mongodump)
mongodump --uri mongodb://localhost:27017 --db ConceptPilot --out ./backup

# Restore if needed
mongorestore ./backup
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Ensure MongoDB is running: `mongod --version` |
| Timeout | Reduce batch size: `--batch-size 50` |
| Permission denied | Check MongoDB user has write permissions |
| Script hangs | Stop with `Ctrl+C` and try with smaller batch |

## Files

- `migrate_narration_script.py` - Main migration script
- `verify_narration_script.py` - Verification/inspection script
- `MIGRATION_NARRATION_SCRIPT.md` - Detailed documentation
- `MIGRATION_README.md` - This file (quick reference)

## Full Documentation

For detailed usage, configuration, and troubleshooting, see: [MIGRATION_NARRATION_SCRIPT.md](MIGRATION_NARRATION_SCRIPT.md)
