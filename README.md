# ConceptPilot 2.0

[![Stars](https://img.shields.io/github/stars/your-org/ConceptPilot2.0?style=social)](https://github.com/your-org/ConceptPilot2.0)
[![Forks](https://img.shields.io/github/forks/your-org/ConceptPilot2.0?style=social)](https://github.com/your-org/ConceptPilot2.0/network/members)

![Demo GIF](./readable_article.html)
Live: [https://your-live-url.com](https://your-live-url.com)

## 🎯 Overview

AI-powered learning platform that generates personalized lessons, quizzes, and flashcards from engineering syllabus topics.

## 🚀 Features

- AI lesson generation with visual board + narration
- Smart flashcards generation (10 cards per request)
- Adaptive quizzes with progress tracking and review flow

## 🛠 Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS, Zustand
- Backend: FastAPI, Python, MongoDB, LangChain, Groq, Deepgram TTS

## 📈 Results

- Personalized learning paths across first-year engineering subjects
- End-to-end flow: onboarding -> lesson -> quiz -> flashcards -> progress

## 🤝 Live | GitHub

[Deploy](https://your-live-url.com) | [Repo Stats](https://github.com/your-org/ConceptPilot2.0)

## 📋 Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### App URLs

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
