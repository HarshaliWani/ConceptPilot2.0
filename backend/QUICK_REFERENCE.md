# FastAPI Development Quick Reference

## Activation & Setup

### Activate Virtual Environment
```powershell
# PowerShell
cd f:\gitH\ConceptPilot2.0\backend
.\venv\Scripts\Activate.ps1

# Command Prompt
cd f:\gitH\ConceptPilot2.0\backend
venv\Scripts\activate.bat
```

## Running the Application (After Main.py Creation)

```bash
# Development with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest app/tests/test_lessons.py

# Run with coverage
pytest --cov=app
```

## Database Operations

### MongoDB Connection Test
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['conceptpilot_db']
print(db.list_collection_names())
```

### Using Motor (Async Driver)
```python
from motor.motor_asyncio import AsyncClient

client = AsyncClient('mongodb://localhost:27017')
db = client['conceptpilot_db']
collection = db['lessons']
```

## Project Packages

### Import Paths
```python
# Models
from app.models.lesson import Lesson
from app.models.user import CustomUser

# Schemas
from app.schemas.lesson import LessonCreate, LessonResponse

# Services
from app.services.lesson_generator import generate_lesson
from app.services.user_service import UserService

# Database
from app.db.mongodb import MongoDB

# Core
from app.core.config import settings
from app.core.security import create_access_token
```

## API Endpoints (Django → FastAPI)

| Operation | Django URL | FastAPI URL | Method |
|-----------|-----------|------------|--------|
| Test Lesson | `/api/lessons/test-lesson/` | `/api/v1/lessons/test-lesson` | GET |
| Generate Lesson | `/api/lessons/generate/` | `/api/v1/lessons/generate` | POST |
| Get Lesson | `/api/lessons/{id}/` | `/api/v1/lessons/{id}` | GET |
| SVG Test | `/api/lessons/svg-test-lesson/` | `/api/v1/lessons/svg-test-lesson` | GET |

## Environment Variables (.env)

Essential configurations:
- `MONGODB_URL` - MongoDB connection string
- `MONGODB_DB_NAME` - Database name
- `SECRET_KEY` - JWT secret (change for production!)
- `GROQ_API_KEY` - Groq LLM API key
- `OPENAI_API_KEY` - OpenAI API key
- `CORS_ORIGINS` - Frontend URLs allowed to access

## Common Tasks

### Install Additional Package
```bash
# While venv is activated
pip install package-name
pip freeze > requirements.txt
```

### Run Database Migrations (for future)
```bash
# When using Alembic (optional future addition)
alembic upgrade head
```

### Check Syntax Errors
```bash
python -m py_compile app/main.py
```

### View Installed Packages
```bash
pip list
pip show fastapi
```

## VSCode Settings (Recommended)

Add to `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.python"
    }
}
```

## FastAPI Documentation

Once the app is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

## Troubleshooting

### ModuleNotFoundError
```bash
# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements.txt
```

### MongoDB Connection Error
```bash
# Check if MongoDB is running
# Use MongoDB Compass or mongosh to test connection
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

## Key Differences: Django → FastAPI

| Aspect | Django | FastAPI |
|--------|--------|---------|
| Routes | `urls.py` | `@router.get()` decorators |
| Models | Django ORM | Pydantic + PyMongo |
| Views | Function/Class-based | Async functions |
| Database | PostgreSQL + ORM | MongoDB + Motor |
| Validation | Forms + Serializers | Pydantic models |
| Docs | Manual | Auto-generated (Swagger) |
| Performance | Good | Excellent (async) |

## Next Phase Tasks

1. Create `app/core/config.py` - Settings management
2. Create `app/core/database.py` - MongoDB connection
3. Create `app/models/` - Pydantic models
4. Create `app/schemas/` - Request/response models
5. Migrate `app/services/lesson_generator.py` from Django
6. Create API endpoints in `app/api/v1/endpoints/`
7. Create `main.py` - FastAPI application

---

**Reference for:** ConceptPilot FastAPI Migration
**Created:** February 6, 2026
