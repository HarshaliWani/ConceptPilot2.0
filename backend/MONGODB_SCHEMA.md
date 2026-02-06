# MongoDB Schema Design for ConceptPilot

## Database: `ConceptPilot`

### Collections Overview

This document describes the MongoDB schema design for the ConceptPilot FastAPI backend, migrated from Django + PostgreSQL.

---

## 1. **users** Collection

Stores user account information and authentication data.

### Schema

```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "name": "John Doe",
  "username": "johndoe",
  "hashed_password": "$2b$12$...",
  "created_at": ISODate("2026-02-06T00:00:00Z"),
  "interests": [
    {
      "_id": ObjectId,
      "interest_category": "sports",
      "specific_interest": "basketball",
      "proficiency_level": "intermediate",
      "created_at": ISODate("2026-02-06T00:00:00Z")
    }
  ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated document ID |
| `email` | String | Yes | User email (unique) |
| `name` | String | Yes | User's full name |
| `username` | String | Yes | Username (unique) |
| `hashed_password` | String | Yes | bcrypt hashed password |
| `created_at` | Date | Yes | Account creation timestamp |
| `interests` | Array | No | Array of user interest documents |

### Indexes

```javascript
// Create unique index on email
db.users.createIndex({ email: 1 }, { unique: true })

// Create unique index on username
db.users.createIndex({ username: 1 }, { unique: true })

// Create index for lookups by email
db.users.createIndex({ email: 1 })
```

### Sample Query

```javascript
// Find user by email
db.users.findOne({ email: "user@example.com" })

// Find user with all their interests
db.users.aggregate([
  { $match: { email: "user@example.com" } },
  { $unwind: "$interests" }
])
```

---

## 2. **lessons** Collection

Stores AI-generated lessons with content and visualization data.

### Schema

```json
{
  "_id": ObjectId,
  "topic": "Newton's Second Law",
  "title": "Dunking Physics: F=ma in Basketball",
  "narration_script": "When LeBron jumps for a dunk...",
  "duration": 12.5,
  "tailored_to_interest": "basketball",
  "audio_url": "https://example.com/audio/lesson1.mp3",
  "board_actions": [
    {
      "type": "text",
      "timestamp": 0,
      "content": "F = ma (Dunking)",
      "x": 300,
      "y": 30,
      "fontSize": 28,
      "fill": "#000"
    },
    {
      "type": "line",
      "timestamp": 2.5,
      "points": [[150, 200], [150, 350]],
      "stroke": "blue",
      "strokeWidth": 3
    },
    {
      "type": "svg_path",
      "timestamp": 5,
      "data": "M400 300 Q400 100 500 100...",
      "stroke": "green",
      "fill": "rgba(0,255,0,0.2)"
    }
  ],
  "raw_llm_output": {
    "topic": "Newton's Second Law",
    "title": "...",
    "narration_script": "...",
    "board_actions": [...],
    "duration": 12.5
  },
  "created_at": ISODate("2026-02-06T00:00:00Z")
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated document ID |
| `topic` | String | Yes | Main topic of the lesson |
| `title` | String | Yes | Lesson title |
| `narration_script` | String | Yes | Full narration text for the lesson |
| `duration` | Float | Yes | Duration in seconds |
| `tailored_to_interest` | String | No | User's interest category used for generation |
| `audio_url` | String | No | URL to audio file |
| `board_actions` | Array | Yes | Array of visualization actions (see below) |
| `raw_llm_output` | Object | No | Full LLM response for debugging |
| `created_at` | Date | Yes | Lesson creation timestamp |

### Board Action Structure

Each board action is a document with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `type` | String | Action type: "text", "line", "rect", "circle", "svg_path" |
| `timestamp` | Float | Time in seconds when action appears |
| `content` | String | Text content (for "text" type) |
| `x`, `y` | Float | X, Y coordinates |
| `points` | Array | Points for lines: [[x1,y1], [x2,y2]] |
| `stroke` | String | Stroke color |
| `strokeWidth` | Float | Stroke width |
| `fill` | String | Fill color |
| `radius` | Float | Radius (for circles) |
| `width`, `height` | Float | Dimensions (for rectangles) |
| `fontSize` | Integer | Font size (for text) |
| `data` | String | SVG path data (for svg_path) |

### Indexes

```javascript
// Create index for topic search
db.lessons.createIndex({ topic: 1 })

// Create index for tailored_to_interest
db.lessons.createIndex({ tailored_to_interest: 1 })

// Create text index for full-text search
db.lessons.createIndex({
  topic: "text",
  title: "text",
  narration_script: "text"
})

// Create compound index for common queries
db.lessons.createIndex({ 
  created_at: -1,
  tailored_to_interest: 1
})
```

### Sample Queries

```javascript
// Find lessons by topic
db.lessons.find({ topic: "Newton's Second Law" })

// Find lessons created in last 7 days
db.lessons.find({
  created_at: {
    $gte: new Date(new Date().getTime() - 7*24*60*60*1000)
  }
})

// Full-text search
db.lessons.find({
  $text: { $search: "physics basketball" }
})

// Get lessons sorted by creation date
db.lessons.find().sort({ created_at: -1 }).limit(10)
```

---

## 3. **user_progress** Collection

Tracks user's progress on individual lessons.

### Schema

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "lesson_id": ObjectId,
  "status": "in_progress",
  "mastery_score": 0.75,
  "time_spent_seconds": 600,
  "created_at": ISODate("2026-02-06T00:00:00Z"),
  "last_accessed": ISODate("2026-02-06T12:30:00Z")
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated document ID |
| `user_id` | ObjectId | Yes | Reference to user document |
| `lesson_id` | ObjectId | Yes | Reference to lesson document |
| `status` | String | Yes | "not_started", "in_progress", or "completed" |
| `mastery_score` | Float | Yes | Score from 0.0 to 1.0 |
| `time_spent_seconds` | Integer | Yes | Total time spent on lesson in seconds |
| `created_at` | Date | Yes | Progress creation timestamp |
| `last_accessed` | Date | Yes | Last access timestamp |

### Indexes

```javascript
// Unique compound index: one progress record per user per lesson
db.user_progress.createIndex(
  { user_id: 1, lesson_id: 1 },
  { unique: true }
)

// Index for finding user's progress
db.user_progress.createIndex({ user_id: 1, last_accessed: -1 })

// Index for finding lesson's progress across users
db.user_progress.createIndex({ lesson_id: 1, status: 1 })

// Index for common queries
db.user_progress.createIndex({ user_id: 1, status: 1 })
```

### Sample Queries

```javascript
// Get user's progress on all lessons
db.user_progress.find({ user_id: ObjectId("...") })

// Get user's progress on specific lesson
db.user_progress.findOne({
  user_id: ObjectId("..."),
  lesson_id: ObjectId("...")
})

// Get all completed lessons for a user
db.user_progress.find({
  user_id: ObjectId("..."),
  status: "completed"
})

// Get recently accessed lessons
db.user_progress.find({
  user_id: ObjectId("...")
}).sort({ last_accessed: -1 }).limit(5)

// Get average mastery score for a lesson
db.user_progress.aggregate([
  { $match: { lesson_id: ObjectId("...") } },
  { $group: {
      _id: "$lesson_id",
      avgMastery: { $avg: "$mastery_score" },
      count: { $sum: 1 }
    }
  }
])
```

---

## Collection Setup Instructions

### Using MongoDB Compass

1. **Connect** to `mongodb://localhost:27017`
2. **Create Database**: `ConceptPilot`
3. **Create Collections**:
   - `users` - for user accounts
   - `lessons` - for generated lessons
   - `user_progress` - for tracking progress

4. **Create Indexes** (via MongoDB Shell or Compass):

```javascript
// Users collection
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ username: 1 }, { unique: true })

// Lessons collection
db.lessons.createIndex({ topic: 1 })
db.lessons.createIndex({ tailored_to_interest: 1 })
db.lessons.createIndex({ created_at: -1 })

// User Progress collection
db.user_progress.createIndex({ user_id: 1, lesson_id: 1 }, { unique: true })
db.user_progress.createIndex({ user_id: 1, last_accessed: -1 })
```

---

## Data Migration from PostgreSQL

### Mapping

| Django Model | PostgreSQL | MongoDB Collection | Notes |
|--------------|-----------|-------------------|-------|
| CustomUser | users | users | Embed interests as array |
| UserInterest | users_userinterest | users.interests | Nested in users doc |
| Lesson | lessons_lesson | lessons | Direct mapping |
| UserProgress | lessons_userprogress | user_progress | ForeignKeys become ObjectId refs |

### Process

1. Export PostgreSQL data to JSON
2. Transform UUIDs to ObjectIds
3. Denormalize UserInterest into users documents
4. Import into MongoDB collections
5. Create indexes
6. Verify data consistency

---

## Notes

- **Denormalization**: `UserInterest` is embedded in `users` documents for better read performance
- **References**: `user_progress` uses `user_id` and `lesson_id` as references (no joins needed in MongoDB)
- **Timestamps**: All dates stored as ISO 8601 format
- **Uniqueness**: Email and username must be unique in `users` collection
- **Compound Uniqueness**: User + Lesson must be unique in `user_progress`

---

**Created:** February 6, 2026
**Status:** Ready for implementation
