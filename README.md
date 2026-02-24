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

---

## 🎯 Core Features Implementation

### 1. **Auto-Trigger Learning Flow**
**Seamless syllabus-to-content generation with zero friction**

**User Journey:**
1. Navigate to **Syllabus Dashboard** → Select subject → module → topic
2. Click **"Start Learning"** → Automatically generates AI lesson on selected topic
3. Click **"Take Quiz"** → Automatically generates personalized quiz

**Technical Implementation:**
- **Session Storage**: Temporary topic storage (`prefilled_topic`, `pending_quiz_topic`)
- **Auto-Navigation**: Instant tab switching and content generation
- **State Management**: Seamless flow between syllabus selection and content creation
- **Loading States**: Smooth transitions with progress indicators

**Files Involved:**
- `ProgressTab.tsx` - Syllabus navigation with auto-trigger buttons
- `ChatInterface.tsx` - Auto-generates lessons from stored topics
- `QuizzesTab.tsx` - Auto-generates quizzes from stored topics

### 2. **Smart Flashcard System**
**AI-generated flashcards with advanced spaced repetition**

**Key Features:**
- **LLM Generation**: Groq-powered flashcard creation with varied difficulty levels
- **3D Flip Animation**: Smooth CSS 3D transforms with backface visibility
- **Confidence Rating**: 5-star rating system (red→orange→yellow→lime→green gradient)
- **Spaced Repetition**: SM-2 algorithm for optimal review scheduling
- **Card Transitions**: Fade animations when navigating between cards

**User Experience:**
- Generate 10 flashcards per topic with one click
- Interactive flip animation (click anywhere on card)
- Rate confidence after revealing answer
- Smooth transitions prevent answer flashing during navigation
- Visual difficulty indicators and progress tracking

**Technical Details:**
- **Animation States**: `isFlipped`, `isAnimating`, `isTransitioning`
- **CSS 3D**: `perspective: 1000px`, `transform-style: preserve-3d`
- **Interaction Prevention**: Disabled states during animations
- **MongoDB Integration**: Async operations with proper error handling

### 3. **Authentication & User Management**
**Secure, seamless authentication with automatic session handling**

**Security Features:**
- **JWT Authentication**: Token-based auth with automatic refresh
- **Global Interceptors**: 401 response handling across all API calls
- **Login Guards**: Automatic redirects for unauthenticated users
- **Session Persistence**: Remember login state across browser sessions

**User Flow:**
1. **Registration** → Profile onboarding (hobbies, course, year)
2. **Auto-login** → Seamless access to personalized dashboard
3. **Token Expiry** → Automatic logout and redirect to login
4. **Profile Updates** → Real-time user data synchronization

**Technical Implementation:**
- **Frontend Guards**: `isLoggedIn()` checks on app initialization
- **API Interceptors**: Axios response interceptors for 401 handling
- **Backend Validation**: `Optional[str] = Header(None)` with 401 responses
- **State Management**: Centralized auth state with clearAuth() functionality

### 4. **Syllabus-Driven Learning**
**Structured curriculum navigation with intelligent content generation**

**Navigation Hierarchy:**
```
Subjects (8 engineering courses)
├── Modules (topics within subject)
    ├── Subtopics (specific learning objectives)
        ├── "Start Learning" → AI Lesson Generation
        └── "Take Quiz" → Adaptive Quiz Creation
```

**Personalization:**
- **Course-Based**: Content tailored to user's engineering course
- **Year-Specific**: Appropriate difficulty for academic year
- **Interest-Aligned**: Hobby-based content recommendations
- **Progress Tracking**: Learning analytics and completion tracking

**Integration Points:**
- **Lesson Generation**: Topics fed to Groq LLM for visual teaching boards
- **Quiz Creation**: Adaptive questions based on syllabus depth
- **Flashcard Topics**: Automatic topic extraction for spaced repetition
- **Progress Analytics**: Completion tracking across all content types

### 5. **AI-Powered Content Generation**
**Multi-modal learning content with advanced AI integration**

**Content Types:**
- **Visual Lessons**: Teaching boards with diagrams and explanations
- **Adaptive Quizzes**: Personalized questions with instant feedback
- **Smart Flashcards**: AI-generated Q&A pairs with difficulty scaling
- **Progress Analytics**: Learning insights and recommendations

**AI Integration:**
- **Groq LLM**: Fast inference for content generation (`llama-3.3-70b-versatile`)
- **Prompt Engineering**: Structured prompts for consistent output quality
- **Error Handling**: Robust fallbacks for API failures
- **Rate Limiting**: Efficient API usage with caching strategies

**Technical Architecture:**
- **Async Processing**: Non-blocking content generation
- **State Management**: Loading states and error boundaries
- **Data Persistence**: MongoDB storage with proper indexing
- **Real-time Updates**: Live progress tracking and notifications

---

## 🚀 Development Session - February 24, 2026

### Recent Fixes & Improvements

This session focused on bug fixes, UI/UX enhancements, and system stability improvements.

#### 🔧 **VSCode Tasks & Environment Fixes**
- **Fixed command duplication** in `tasks.json` - removed redundant command/args combinations
- **Corrected venv paths** - standardized to use root `.venv` directory
- **Updated MongoDB task** - fixed path to `D:\sarthak\tools\mongoDBServer\bin\mongod.exe`
- **Parallel task execution** - all compound tasks now run simultaneously with `dependsOrder: "parallel"`

#### 🎨 **Frontend Build & Error Fixes**
- **Removed dead code** - cleaned up 316 lines of duplicate component code in `FlashcardsTab.tsx`
- **Fixed Suspense boundaries** - added `<Suspense>` wrappers to prevent `useSearchParams()` errors in:
  - `app/page.tsx`
  - `app/quiz/page.tsx`
  - `app/lesson/page.tsx`
  - `src/app/lesson/page.tsx`

#### 🔐 **Authentication System**
- **Implemented auth guards** - added login redirects for unauthenticated users
- **Global 401 interceptor** - automatic logout and redirect on expired tokens
- **Backend auth validation** - fixed `Header(...)` to `Optional[str] = Header(None)` with proper 401 responses
- **Frontend auth state** - added `isLoggedIn()` checks and token management

#### ⚡ **Auto-Trigger Features**
- **Syllabus integration** - "Start Learning" automatically generates and navigates to lessons
- **Quiz auto-generation** - "Take Quiz" creates quizzes from selected topics
- **Session storage** - temporary topic storage for seamless navigation flow

#### 🧠 **Flashcard System Fixes**
- **Backend LLM integration** - fixed `langchain_core.prompts` import and model configuration
- **API key resolution** - corrected `settings.groq_api_key` attribute access
- **MongoDB operations** - replaced `insert_one()` with `create()` method
- **Response handling** - proper ID extraction from MongoDB operations

#### 🎴 **Flashcard UI/UX Improvements**
- **3D Flip Animation** - replaced broken Tailwind classes with proper CSS `transform-style: preserve-3d`
- **Smooth transitions** - increased duration to 700ms with `ease-in-out` easing
- **Text selection prevention** - added `select-none` to prevent accidental text highlighting
- **Double-click prevention** - animation state management prevents rapid clicking
- **Rating colors** - improved star rating colors (red→orange→yellow→lime→green gradient)

#### 🎭 **Card Transition Animations**
- **Smooth navigation** - added fade transitions when changing cards (350ms opacity animation)
- **State management** - `isTransitioning` state prevents interactions during card changes
- **Visual feedback** - navigation buttons disabled during transitions
- **Emoji cleanup** - removed lightbulb emoji (ðŸ’¡) from flashcard explanations

#### 🏗️ **System Stability**
- **Error handling** - comprehensive error boundaries and loading states
- **State synchronization** - proper cleanup and state resets
- **Performance** - optimized animations and prevented unnecessary re-renders
- **Build verification** - all changes tested with successful `npm run build`

### Files Modified
```
frontend/app/components/FlashcardsTab.tsx    # Major UI/UX improvements
frontend/app/page.tsx                       # Auth guard + Suspense
frontend/app/quiz/page.tsx                  # Suspense boundary
frontend/app/lesson/page.tsx                # Suspense boundary
frontend/src/app/lesson/page.tsx            # Suspense boundary
frontend/src/services/api.ts                # 401 interceptor
frontend/app/components/ChatInterface.tsx   # Auto-trigger logic
frontend/app/components/ProgressTab.tsx     # Session storage integration
frontend/app/components/QuizzesTab.tsx      # Auto-quiz generation
backend/app/api/v1/endpoints/flashcards.py  # MongoDB operations fix
backend/app/api/v1/endpoints/auth.py        # Auth validation
backend/app/services/flashcard_generator.py # LLM configuration
.vscode/tasks.json                          # Task configuration fixes
```

### Key Technical Achievements
- ✅ **Zero build errors** - all TypeScript and Python code compiles cleanly
- ✅ **Smooth animations** - professional-grade card flip and transition effects
- ✅ **Robust auth flow** - seamless login/logout with proper error handling
- ✅ **Auto-learning flow** - one-click lesson and quiz generation from syllabus
- ✅ **Enhanced UX** - prevented common interaction issues (double-clicks, text selection)
- ✅ **System reliability** - comprehensive error handling and state management

All changes maintain backward compatibility and follow existing code patterns and conventions.
