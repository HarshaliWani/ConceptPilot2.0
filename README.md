# ConceptPilot2.0

An AI-powered educational platform that generates personalized lessons with visual teaching boards, quizzes, flashcards, and progress tracking.

## Features

- 🎓 **AI Teaching Board**: Interactive lessons with visual diagrams and narration
- 📝 **Adaptive Quizzes**: Personalized quizzes based on your learning progress
- 🎴 **Smart Flashcards**: LLM-generated flashcards with spaced repetition algorithm
- 📊 **Syllabus Dashboard**: Organized learning paths based on first-year engineering curriculum
- 👤 **Profile Onboarding**: Personalized learning based on hobbies, course, and year
- 📈 **Progress Tracking**: Monitor your learning journey with detailed analytics

## Tech Stack

**Backend:**
- FastAPI (Python)
- MongoDB (Motor async driver)
- LangChain + Groq LLM
- Deepgram Text-to-Speech
- Pydantic for validation

**Frontend:**
- Next.js 14 (App Router)
- React + TypeScript
- Tailwind CSS
- Zustand for state management
- Axios for API calls

## Quick Start with VSCode Tasks

The easiest way to start the entire application is using the built-in VSCode tasks:

### 1. Using VSCode Command Palette

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task"
3. Select **"🚀 Start All Servers"** to start backend and frontend
   - Or select **"🚀 Start All (with MongoDB)"** if you need to start MongoDB locally

### 2. Using Keyboard Shortcut

1. Press `Ctrl+Shift+B` (default build task)
2. The servers will start automatically in separate terminal panels

### Available Tasks

- **Start Backend (FastAPI)**: Starts the FastAPI server on port 8000
- **Start Frontend (Next.js)**: Starts the Next.js dev server on port 3000
- **Start MongoDB (Local)**: Starts MongoDB with local data directory
- **🚀 Start All Servers**: Starts backend and frontend simultaneously
- **🚀 Start All (with MongoDB)**: Starts all services including MongoDB
- **Install Backend Dependencies**: Runs `pip install -r requirements.txt`
- **Install Frontend Dependencies**: Runs `npm install`

## Manual Setup

If you prefer to start services manually:

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB (local or cloud)
- Groq API Key
- Deepgram API Key

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create .env file with:
# GROQ_API_KEY=your_key
# DEEPGRAM_API_KEY=your_key
# MONGODB_URL=mongodb://localhost:27017

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Debugging

Use the built-in debug configurations:

1. Press `F5` or go to Run and Debug panel
2. Select "🚀 Debug Full Stack" to debug both backend and frontend
3. Set breakpoints in your code

### Individual Debug Configurations

- **Backend: FastAPI Debugger**: Debug Python backend only
- **Frontend: Next.js Debugger**: Debug Next.js frontend only

## Project Structure

```
ConceptPilot2.0/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API endpoints
│   │   ├── core/                # Config, database, security
│   │   ├── models/              # Pydantic models
│   │   ├── schemas/             # Request/response schemas
│   │   ├── services/            # Business logic (LLM, TTS, flashcards)
│   │   └── main.py              # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── components/          # React components
│   │   ├── login/               # Login/register page
│   │   ├── quiz/                # Quiz page
│   │   └── page.tsx             # Main app page
│   ├── src/
│   │   ├── lib/                 # Auth helpers
│   │   └── services/            # API service layer
│   ├── public/
│   │   └── syllabus.json        # First-year curriculum
│   └── package.json
└── .vscode/
    ├── tasks.json               # VSCode tasks for starting servers
    ├── launch.json              # Debug configurations
    └── settings.json            # Workspace settings
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create new account
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update profile

### Lessons
- `POST /api/v1/lessons/generate` - Generate AI lesson
- `GET /api/v1/lessons/` - List lessons
- `GET /api/v1/lessons/{id}` - Get lesson details

### Quizzes
- `POST /api/v1/quizzes/generate` - Generate quiz
- `GET /api/v1/quizzes/` - List quizzes
- `POST /api/v1/quizzes/{id}/submit` - Submit quiz
- `GET /api/v1/quizzes/attempts/user/{user_id}` - Get user attempts

### Flashcards
- `POST /api/v1/flashcards/generate` - Generate 10 flashcards with LLM
- `GET /api/v1/flashcards/` - Get flashcards (with filters)
- `GET /api/v1/flashcards/topics` - Get unique topics
- `PUT /api/v1/flashcards/{id}/review` - Review flashcard (spaced repetition)
- `DELETE /api/v1/flashcards/{id}` - Delete flashcard

## Key Features Implementation

### 1. Profile Onboarding
After registration, users are redirected to the profile tab to complete:
- Hobby/Interest (for personalized lessons)
- Course Code (8 first-year courses available)
- Year of Study (1-4)

### 2. Syllabus Dashboard
Interactive 3-level navigation:
- **Subjects** → 8 first-year engineering subjects
- **Modules** → Topics within each subject
- **Subtopics** → "Start Learning" or "Take Quiz" for each

### 3. Flashcards with Spaced Repetition
- Generate flashcards from syllabus topics or custom input
- LLM generates 10 cards with varied difficulty
- SM-2 spaced repetition algorithm
- 5-star confidence rating system
- Tracks next review date and ease factor

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with FastAPI and Next.js
- Powered by Groq LLM and Deepgram TTS
- Spaced repetition algorithm based on SM-2
