# ConceptPilot 2.0 - Architecture & Implementation Plan

> **Last Updated:** February 9, 2026

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Current Architecture](#current-architecture)
4. [Backend Implementation](#backend-implementation)
5. [Frontend Implementation](#frontend-implementation)
6. [Database Schema](#database-schema)
7. [Future Features Plan](#future-features-plan)
8. [Implementation Roadmap](#implementation-roadmap)

---

## Project Overview

**ConceptPilot** is an AI-powered adaptive learning platform that generates personalized lessons with animated visualizations. The platform tailors educational content to users' interests, making complex concepts easier to understand through relatable examples.

### Core Features (Current)
- AI-generated lessons using Groq LLM
- Animated whiteboard visualizations (text, lines, shapes, SVG paths)
- Audio narration with synchronized board actions
- User authentication (register/login with JWT)
- Lesson storage and retrieval

### Planned Features
- Quiz system for knowledge assessment
- Cheat sheet generator for quick revision
- YouTube video integration for supplementary learning

---

## Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Primary language |
| FastAPI | 0.104.1 | Web framework |
| Motor | 3.3.2 | Async MongoDB driver |
| Pydantic | 2.7+ | Data validation |
| LangChain | Latest | LLM orchestration |
| LangChain-Groq | Latest | Groq LLM integration |
| python-jose | 3.3.0 | JWT authentication |
| passlib + bcrypt | 1.7.4 | Password hashing |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.1.4 | React framework |
| React | 19.2.3 | UI library |
| TypeScript | 5.x | Type safety |
| Konva + react-konva | 10.2.0 | Canvas animations |
| Zustand | 5.0.10 | State management |
| Axios | 1.13.2 | HTTP client |
| Tailwind CSS | 4.x | Styling |

### Database
| Technology | Purpose |
|------------|---------|
| MongoDB | Document database |
| MongoDB Compass | GUI for database management |

### AI/LLM
| Provider | Model | Purpose |
|----------|-------|---------|
| Groq | meta-llama/llama-4-scout-17b-16e-instruct | Lesson generation |

---

## Current Architecture

```
ConceptPilot2.0/
├── backend/                     # FastAPI Python Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Application entry point
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py       # Router aggregation
│   │   │       └── endpoints/
│   │   │           ├── auth.py      # Authentication endpoints
│   │   │           └── lessons.py   # Lesson CRUD endpoints
│   │   ├── core/
│   │   │   ├── config.py        # Environment settings
│   │   │   ├── database.py      # MongoDB connection manager
│   │   │   └── security.py      # JWT & password utilities
│   │   ├── db/
│   │   │   └── mongodb.py       # Generic CRUD operations
│   │   ├── models/
│   │   │   ├── lesson.py        # Lesson document models
│   │   │   ├── progress.py      # User progress models
│   │   │   └── user.py          # User document models
│   │   ├── schemas/
│   │   │   ├── lesson.py        # Lesson API schemas
│   │   │   ├── progress.py      # Progress API schemas
│   │   │   └── user.py          # User API schemas
│   │   ├── services/
│   │   │   └── lesson_generator.py  # AI lesson generation
│   │   └── utils/
│   │       └── exceptions.py    # Custom exceptions
│   ├── requirements.txt
│   ├── MONGODB_SCHEMA.md
│   └── QUICK_REFERENCE.md
│
└── frontend/                    # Next.js TypeScript Frontend
    ├── app/
    │   ├── layout.tsx           # Root layout
    │   ├── page.tsx             # Home page
    │   ├── generate/
    │   │   └── page.tsx         # Lesson generation form
    │   └── lesson/
    │       └── page.tsx         # Lesson viewer (duplicate)
    ├── src/
    │   ├── app/
    │   │   └── lesson/
    │   │       └── page.tsx     # Lesson player page
    │   ├── components/
    │   │   ├── AudioController.tsx   # Audio playback controls
    │   │   └── LessonCanvas.tsx      # Animated whiteboard
    │   ├── services/
    │   │   └── api.ts           # Backend API client
    │   └── store/
    │       └── lessonStore.ts   # Zustand state management
    ├── package.json
    └── tsconfig.json
```

---

## Backend Implementation

### Entry Point: `main.py`

```python
# Application lifecycle:
# 1. FastAPI app initialization with CORS middleware
# 2. MongoDB connection on startup
# 3. API router registration at /api/v1
# 4. MongoDB disconnection on shutdown
```

**Key Responsibilities:**
- CORS configuration for local development
- Database lifecycle management
- Route mounting

---

### Core Module: `app/core/`

#### `config.py` - Settings Management
Loads configuration from environment variables using Pydantic Settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `mongodb_url` | `mongodb://localhost:27017` | MongoDB connection string |
| `mongodb_db_name` | `ConceptPilot` | Database name |
| `secret_key` | (change in prod) | JWT signing key |
| `access_token_expire_minutes` | 30 | Token expiration |
| `groq_api_key` | "" | Groq LLM API key |

#### `database.py` - MongoDB Connection Manager
Singleton pattern for database connections:

```python
class MongoDB:
    client: AsyncIOMotorClient  # Motor async client
    db: AsyncIOMotorDatabase    # Database reference
    
    @classmethod
    async def connect_db(cls) -> None:
        # Connects to MongoDB, verifies with ping
    
    @classmethod
    async def close_db(cls) -> None:
        # Closes connection gracefully
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        # Returns database instance (dependency injection)
```

#### `security.py` - Authentication Utilities

| Function | Purpose |
|----------|---------|
| `get_password_hash(password)` | Hash password with bcrypt |
| `verify_password(plain, hashed)` | Verify password against hash |
| `create_access_token(subject, expires_delta)` | Generate JWT token |
| `decode_access_token(token)` | Decode and validate JWT |

---

### Database Layer: `app/db/mongodb.py`

Generic CRUD operations class:

```python
class MongoDBOperations:
    def __init__(self, db, collection_name):
        self.collection = db[collection_name]
    
    async def create(document) -> str          # Insert document, return ID
    async def read_by_id(doc_id) -> dict       # Find by ObjectId
    async def read_many(query, skip, limit)    # Paginated query
    async def update(doc_id, update_data)      # Update fields
    async def delete(doc_id) -> bool           # Remove document
    async def find_one(query) -> dict          # Find single match
```

---

### API Endpoints: `app/api/v1/endpoints/`

#### Authentication (`auth.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Create new user account |
| `/api/v1/auth/login` | POST | Authenticate and get JWT |

**Register Flow:**
1. Check email uniqueness
2. Check username uniqueness
3. Hash password with bcrypt
4. Store user document
5. Return user data (without password)

**Login Flow:**
1. Find user by email
2. Verify password
3. Generate JWT token
4. Return token + user info

#### Lessons (`lessons.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/lessons/generate` | POST | Generate new AI lesson |
| `/api/v1/lessons/{lesson_id}` | GET | Fetch lesson by ID |
| `/api/v1/lessons/` | GET | List all lessons (paginated) |

**Generate Flow:**
1. Receive topic, user_interest, proficiency_level
2. Call `lesson_generator.generate_lesson()`
3. Add timestamp
4. Store in MongoDB
5. Return lesson with generated ID

---

### Services: `app/services/lesson_generator.py`

The AI-powered lesson generation service:

```python
async def generate_lesson(topic, user_interest, proficiency_level) -> Dict:
    """
    Workflow:
    1. Check for GROQ API key
    2. If missing: return mock lesson (for development)
    3. Build LangChain prompt template
    4. Initialize ChatGroq LLM
    5. Invoke chain and parse response
    6. Handle JSON parsing (remove markdown, extract nested objects)
    7. Return structured lesson data
    """
```

**Output Structure:**
```json
{
  "topic": "Newton's Second Law",
  "title": "Dunking Physics: F=ma in Basketball",
  "narration_script": "When LeBron jumps for a dunk...",
  "duration": 12.5,
  "tailored_to_interest": "basketball",
  "board_actions": [
    {
      "type": "text",
      "timestamp": 0,
      "content": "F = ma",
      "x": 300, "y": 30,
      "fontSize": 28, "fill": "#000"
    },
    {
      "type": "line",
      "timestamp": 2.5,
      "points": [[150, 200], [150, 350]],
      "stroke": "blue",
      "strokeWidth": 3
    }
  ],
  "raw_llm_output": { ... }
}
```

**Fallback Handling:**
- No API key → Mock lesson
- LLM initialization fails → Mock lesson
- JSON parse error → Extract with regex or return raw

---

### Models: `app/models/`

#### `user.py`
```python
CustomUser:
  - id: ObjectId
  - email: EmailStr (unique)
  - name: str
  - username: str (unique)
  - hashed_password: str
  - interests: List[UserInterest]
  - created_at: datetime

UserInterest:
  - interest_category: str
  - specific_interest: str
  - proficiency_level: str
```

#### `lesson.py`
```python
Lesson:
  - id: ObjectId
  - topic: str
  - title: str
  - narration_script: str
  - duration: float
  - tailored_to_interest: str
  - audio_url: str (optional)
  - board_actions: List[BoardAction]
  - raw_llm_output: Dict
  - created_at: datetime

BoardAction:
  - type: str (text|line|rect|circle|svg_path)
  - timestamp: float
  - content, x, y, points, stroke, fill, etc.
```

#### `progress.py`
```python
UserProgress:
  - id: ObjectId
  - user_id: ObjectId
  - lesson_id: ObjectId
  - status: str (not_started|in_progress|completed)
  - mastery_score: float (0.0-1.0)
  - time_spent_seconds: int
  - created_at, last_accessed: datetime
```

---

## Frontend Implementation

### State Management: `lessonStore.ts`

Zustand store for lesson playback state:

```typescript
interface LessonStore {
  // State
  lessonData: LessonData | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  audioElement: HTMLAudioElement | null;
  
  // Actions
  setLessonData(data): void;
  setIsPlaying(playing): void;
  setCurrentTime(time): void;
  setDuration(duration): void;
  resetPlayback(): void;
}
```

---

### API Client: `api.ts`

```typescript
const baseURL = 'http://localhost:8000/api/v1';

// Available functions:
fetchTestLesson(): Promise<LessonData>     // Get test lesson
fetchLesson(id): Promise<LessonData>       // Get lesson by ID
generateLesson(payload): Promise<LessonData> // Generate new lesson
```

---

### Components

#### `LessonCanvas.tsx` - Animated Whiteboard

Uses react-konva for canvas rendering:

```typescript
// Renders board_actions based on currentTime
// Filters actions where timestamp <= currentTime
// Supports: text, line, rect, circle, svg_path
```

**Rendering Logic:**
1. Subscribe to `currentTime` from Zustand store
2. Filter `board_actions` by timestamp
3. Render each action type using Konva shapes

#### `AudioController.tsx` - Playback Controls

Handles both real audio and mock playback:

```typescript
// If audio_url exists: use HTMLAudioElement
// If no audio: simulate playback with setInterval

// Updates currentTime → triggers LessonCanvas re-render
// Provides play/pause, seek, duration display
```

---

### Pages

#### `/generate` - Lesson Generation Form

```tsx
// Form fields:
// - Topic (text input)
// - User Interest (text input)
// - Proficiency Level (select: beginner|intermediate|advanced)

// On submit:
// 1. Call generateLesson() API
// 2. Redirect to /lesson?id={lesson._id}
```

#### `/lesson` - Lesson Player

```tsx
// URL params: ?id={lessonId}

// On mount:
// 1. Fetch lesson by ID (or test lesson if no ID)
// 2. Store in Zustand
// 3. Render LessonCanvas + AudioController

// On unmount:
// - Reset playback state
```

---

## Database Schema

### Collections

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `users` | User accounts | email, username, password_hash, interests[] |
| `lessons` | Generated lessons | topic, title, narration_script, board_actions[] |
| `user_progress` | Learning progress | user_id, lesson_id, status, mastery_score |

### Indexes

```javascript
// users
{ email: 1 }        // unique
{ username: 1 }     // unique

// lessons
{ topic: 1 }
{ created_at: -1 }
{ topic: "text", title: "text", narration_script: "text" }

// user_progress
{ user_id: 1, lesson_id: 1 }  // unique compound
{ user_id: 1, status: 1 }
```

---

## Future Features Plan

### 1. Quiz System with Adaptive Proficiency Tracking (Priority: High)

AI-generated quizzes to assess understanding after lessons. Quiz results dynamically update user proficiency levels based on performance:
- **Proficiency Increase**: Answering hard/medium questions correctly boosts topic proficiency
- **Proficiency Decrease**: Failing easy questions reduces topic proficiency
- **Smart Evaluation**: System tracks per-topic proficiency in user profile for personalized lesson generation

#### New Files to Create

**Backend:**
| File | Purpose |
|------|---------|
| `app/models/quiz.py` | Quiz and QuizAttempt models |
| `app/schemas/quiz.py` | Request/response schemas |
| `app/services/quiz_generator.py` | AI quiz generation using Groq |
| `app/api/v1/endpoints/quizzes.py` | Quiz CRUD endpoints |

**Frontend:**
| File | Purpose |
|------|---------|
| `app/quiz/page.tsx` | Quiz taking interface |
| `src/components/QuizCard.tsx` | Question display |
| `src/components/QuizResults.tsx` | Score and review |
| `src/components/QuizTimer.tsx` | Countdown timer |

#### New Database Schema

```json
// quizzes collection
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "lesson_id": ObjectId,
  "topic": "String",
  "questions": [
    {
      "id": "1",
      "question": "What is...?",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": 0,
      "difficulty": "easy",
      "explanation": {
        "correct": "Because...",
        "incorrect": { "0": "...", "1": "...", "2": "...", "3": "..." }
      }
    }
  ],
  "created_at": ISODate
}

// quiz_attempts collection
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "quiz_id": ObjectId,
  "lesson_id": ObjectId,
  "topic": "String",
  "answers": { "1": 0, "2": 2 },
  "score": 75.0,
  "correct_count": 6,
  "wrong_count": 2,
  "performance_by_difficulty": {
    "easy": { "correct": 3, "total": 3 },
    "medium": { "correct": 2, "total": 3 },
    "hard": { "correct": 1, "total": 2 }
  },
  "proficiency_change": 0.1,  // Calculated proficiency adjustment
  "time_taken_seconds": 420,
  "completed_at": ISODate
}

// users collection (updated)
{
  "_id": ObjectId,
  "email": "user@example.com",
  "name": "String",
  "username": "String",
  "hashed_password": "String",
  "interests": [...],
  "topic_proficiency": {  // NEW: Track proficiency per topic
    "Python Basics": {
      "level": "intermediate",  // beginner|intermediate|advanced
      "score": 0.65,  // 0.0-1.0 proficiency score
      "quizzes_taken": 3,
      "last_updated": ISODate
    },
    "Data Structures": {
      "level": "beginner",
      "score": 0.35,
      "quizzes_taken": 1,
      "last_updated": ISODate
    }
  },
  "created_at": ISODate
}
```

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/quizzes/generate` | POST | Generate quiz for topic |
| `/api/v1/quizzes/{id}` | GET | Get quiz by ID |
| `/api/v1/quizzes/{id}/submit` | POST | Submit quiz answers |
| `/api/v1/quizzes/attempts` | GET | Get user's quiz history |

#### Quiz Generation Prompt (Reference)
```
Generate 8 MCQ questions:
- 3 Easy (basic recall)
- 3 Medium (understanding/application)
- 2 Hard (analysis/problem-solving)

Each question has:
- 4 options
- Correct answer index (0-3)
- Detailed explanation for correct answer
- Brief explanation for each incorrect option
```

#### Proficiency Tracking Algorithm

After each quiz attempt, user proficiency is updated:

**Proficiency Change Calculation:**
```python
# Performance weights by difficulty
difficulty_weights = {
    "easy": 0.5,     # Lower impact
    "medium": 1.0,   # Standard impact
    "hard": 1.5      # Higher impact
}

# Calculate weighted performance
for difficulty in ["easy", "medium", "hard"]:
    correct = performance[difficulty]["correct"]
    total = performance[difficulty]["total"]
    
    if total > 0:
        accuracy = correct / total
        # Penalty for failing easy, bonus for acing hard
        if difficulty == "easy" and accuracy < 0.67:
            proficiency_change -= 0.1 * difficulty_weights[difficulty]
        elif difficulty == "hard" and accuracy >= 0.5:
            proficiency_change += 0.15 * difficulty_weights[difficulty]
        elif difficulty == "medium":
            proficiency_change += (accuracy - 0.5) * difficulty_weights[difficulty] * 0.1

# Update user's topic proficiency (0.0 to 1.0 scale)
new_score = clamp(current_score + proficiency_change, 0.0, 1.0)
new_level = "beginner" if new_score < 0.4 else "intermediate" if new_score < 0.7 else "advanced"
```

**Proficiency Levels:**
- Beginner: 0.0 - 0.39
- Intermediate: 0.4 - 0.69
- Advanced: 0.7 - 1.0

---

### 2. Cheat Sheet Generator (Priority: Medium)

AI-generated condensed study notes in markdown format.

#### New Files to Create

**Backend:**
| File | Purpose |
|------|---------|
| `app/models/cheat_sheet.py` | CheatSheet model |
| `app/schemas/cheat_sheet.py` | Request/response schemas |
| `app/services/cheat_sheet_generator.py` | AI generation service |
| `app/api/v1/endpoints/cheat_sheets.py` | CRUD endpoints |

**Frontend:**
| File | Purpose |
|------|---------|
| `app/cheatsheet/page.tsx` | Cheat sheet viewer |
| `src/components/CheatSheetViewer.tsx` | Markdown renderer |

#### New Database Schema

```json
// cheat_sheets collection
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "lesson_id": ObjectId,
  "topic": "String",
  "content": "# Markdown content...",
  "created_at": ISODate
}
```

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cheat-sheets/generate` | POST | Generate cheat sheet |
| `/api/v1/cheat-sheets/` | GET | List user's cheat sheets |
| `/api/v1/cheat-sheets/{id}` | GET | Get cheat sheet by ID |

---

### 3. YouTube Integration (Priority: Low)

Fetch relevant YouTube videos for lesson topics.

#### New Files to Create

**Backend:**
| File | Purpose |
|------|---------|
| `app/services/youtube_service.py` | YouTube API integration |

**Frontend:**
| File | Purpose |
|------|---------|
| `src/components/YouTubeEmbed.tsx` | Video player embed |

#### Integration Points
- Add `youtube_videos` field to lesson response
- Display related videos on lesson page
- Use YouTube Data API v3

#### Dependencies
```
# Backend
google-api-python-client
```

---

## Implementation Roadmap

### Sprint 1: Quiz System - Backend (Week 1)

| Task | Priority |
|------|----------|
| Create `app/models/quiz.py` with Quiz and QuizAttempt models | High |
| Create `app/schemas/quiz.py` with request/response schemas | High |
| Implement `app/services/quiz_generator.py` using Groq | High |
| Create `app/api/v1/endpoints/quizzes.py` with CRUD | High |
| Add quiz routes to `app/api/v1/api.py` | High |
| Test quiz generation with various topics | High |

### Sprint 2: Quiz System - Frontend (Week 2)

| Task | Priority |
|------|----------|
| Create `/quiz` page with question display | High |
| Build QuizCard component with options | High |
| Add timer functionality | Medium |
| Build QuizResults component with score | High |
| Add review mode with explanations | Medium |
| Connect to lesson flow (quiz after lesson) | High |

### Sprint 3: Cheat Sheet + YouTube (Week 3)

| Task | Priority |
|------|----------|
| Implement cheat sheet generator service | Medium |
| Create cheat sheet endpoints | Medium |
| Build markdown viewer component | Medium |
| Add `react-markdown` to frontend | Medium |
| Set up YouTube API service | Low |
| Add video suggestions to lesson page | Low |

---

## Dependencies to Add

### Backend (`requirements.txt`)
```
# For YouTube integration
google-api-python-client

# Already have LangChain for AI generation
```

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "react-markdown": "^9.x",    // Cheat sheet rendering
    "lucide-react": "^0.x"       // Icons
  }
}
```

---

## Environment Variables

```env
# .env file (backend)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ConceptPilot
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-key
YOUTUBE_API_KEY=your-youtube-key  # Future
```

---

## API Summary

### Current Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT |
| POST | `/api/v1/lessons/generate` | Generate AI lesson |
| GET | `/api/v1/lessons/{id}` | Get lesson by ID |
| GET | `/api/v1/lessons/` | List all lessons |

### Planned Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/quizzes/generate` | Generate quiz |
| GET | `/api/v1/quizzes/{id}` | Get quiz |
| POST | `/api/v1/quizzes/{id}/submit` | Submit answers |
| GET | `/api/v1/quizzes/attempts` | Get attempt history |
| POST | `/api/v1/cheat-sheets/generate` | Generate cheat sheet |
| GET | `/api/v1/cheat-sheets/` | List cheat sheets |
| GET | `/api/v1/cheat-sheets/{id}` | Get cheat sheet |

---

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Add GROQ_API_KEY to .env
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### MongoDB
1. Install MongoDB locally
2. Start MongoDB service
3. Create `ConceptPilot` database
4. Collections created automatically on first use

---

**Document Status:** Complete
**Next Step:** Begin Sprint 1 - Quiz System Backend
