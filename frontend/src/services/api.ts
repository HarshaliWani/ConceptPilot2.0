// frontend/src/services/api.ts
import axios from 'axios';
import { getToken, clearAuth } from '../lib/auth';

const baseURL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL,
  timeout: 200000, // Increased to 200 seconds for lesson generation + TTS
});

// Attach auth token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401 (missing or invalid token)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (typeof window !== 'undefined' && error?.response?.status === 401) {
      clearAuth();
      window.location.replace('/login');
    }
    return Promise.reject(error);
  }
);


// ========== Auth API Functions ==========

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    _id: string;
    email: string;
    name: string;
    username: string;
    grade_level?: string;
    topic_proficiency?: Record<string, number>;
  };
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', { email, password });
  return response.data;
}

export interface RegisterPayload {
  email: string;
  name: string;
  username: string;
  password: string;
  grade_level?: string;
}

export async function register(payload: RegisterPayload) {
  const response = await apiClient.post('/auth/register', payload);
  return response.data;
}

export async function fetchCurrentUser() {
  const response = await apiClient.get('/auth/me');
  return response.data;
}

export async function updateProfile(updates: Partial<{
  name: string;
  email: string;
  username: string;
  password: string;
  grade_level: string;
  hobby: string;
  course_code: string;
  year: number;
}>) {
  const response = await apiClient.put('/auth/me', updates);
  return response.data;
}


export interface LessonData {
  _id: string;
  topic: string;
  title: string;
  narration_script: string;
  board_actions: Array<{ timestamp: number; type: string; [key: string]: any }>;
  audio_url: string | null;
  duration: number;
  created_at: string;
  tailored_to_interest: string;
  raw_llm_output: Record<string, any>;
  word_timestamps?: Array<{ word: string; start: number; end: number }>;
  board_actions_synced?: Array<{ timestamp: number; type: string; [key: string]: any }>;
  // Batch/playlist metadata
  batch_id?: string;
  batch_index?: number;
  batch_total?: number;
}


// ========== Streaming Audio & Timestamps API Functions ==========

/**
 * Get the streaming audio URL for a lesson.
 * This endpoint streams audio chunks in real-time, reducing latency from 60s to <3s.
 */
export function getStreamingAudioUrl(lessonId: string): string {
  return `${baseURL}/lessons/${lessonId}/audio/stream`;
}

/**
 * Fetch word-level timestamps for a lesson using Groq Whisper.
 * Enables perfect synchronization between audio and canvas animations.
 */
export interface TimestampsResponse {
  lesson_id: string;
  audio_url: string;
  duration: number;
  word_count: number;
  word_timestamps: Array<{ word: string; start: number; end: number }>;
  board_actions_synced: Array<{ timestamp: number; type: string; [key: string]: any }>;
  message: string;
}

export async function fetchWordTimestamps(lessonId: string): Promise<TimestampsResponse> {
  try {
    const response = await apiClient.get<TimestampsResponse>(`/lessons/${lessonId}/timestamps`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching timestamps for lesson ${lessonId}:`, error);
    throw error;
  }
}


// Fetch a test lesson (gets the first available lesson with full details)
export async function fetchTestLesson(): Promise<LessonData> {
  try {
    // First get the list of lessons to find an ID
    const listResponse = await apiClient.get<Array<{_id: string}>>('/lessons/?limit=1');
    if (listResponse.data && listResponse.data.length > 0) {
      const lessonId = listResponse.data[0]._id;
      // Then fetch the full lesson details
      return fetchLesson(lessonId);
    }
    throw new Error('No lessons available. Please generate a lesson first.');
  } catch (error) {
    console.error('Error fetching test lesson:', error);
    throw error;
  }
}


export async function fetchLesson(lessonId: string): Promise<LessonData> {
  try {
    const response = await apiClient.get<LessonData>(`/lessons/${lessonId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching lesson with ID ${lessonId}:`, error);
    throw error;
  }
}

// Generate a new lesson
export interface GenerateLessonPayload {
  topic: string;
  user_interest: string;
  proficiency_level: string;
}

export async function generateLesson(payload: GenerateLessonPayload): Promise<LessonData> {
  try {
    const response = await apiClient.post<LessonData>('/lessons/generate', payload);
    return response.data;
  } catch (error) {
    console.error('Error generating lesson:', error);
    throw error;
  }
}

// Generate batch of lessons for playlist
export interface BatchLessonResponse {
  batch_id: string;
  total_lessons: number;
  lessons: LessonData[];
  playlist_order: string[];
}

export async function generateBatchLessons(
  topics: string[],
  user_interest: string,
  proficiency_level: string = 'beginner',
  grade_level: string = 'middle school'
): Promise<BatchLessonResponse> {
  try {
    // Batch generation can take 5-10 minutes per lesson with TTS
    // Set timeout to 30 minutes for up to ~10 lessons
    const response = await apiClient.post<BatchLessonResponse>(
      '/lessons/generate/batch',
      {
        topics,
        user_interest,
        proficiency_level,
        grade_level,
      },
      {
        timeout: 1800000, // 30 minutes
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error generating batch lessons:', error);
    throw error;
  }
}

// Generate batch lessons with progressive streaming (SSE)
export interface BatchStreamCallbacks {
  onLesson: (lesson: LessonData, index: number) => void;
  onComplete: (batchId: string, total: number) => void;
  onError: (topic: string, error: string) => void;
}

export function generateBatchLessonsStream(
  topics: string[],
  user_interest: string,
  proficiency_level: string = 'beginner',
  grade_level: string = 'middle school',
  callbacks: BatchStreamCallbacks
): () => void {
  const token = getToken();
  
  // Build query string
  const params = new URLSearchParams({
    topics: topics.join(','),
    user_interest,
    proficiency_level,
    grade_level,
  });
  
  const url = `${baseURL}/lessons/generate/batch/stream?${params}`;
  
  console.log('[SSE] Connecting to batch stream:', url);
  
  // Create EventSource connection
  const eventSource = new EventSource(url, {
    withCredentials: false,
  });
  
  // Handle lesson events
  eventSource.addEventListener('lesson', (event) => {
    try {
      const lesson = JSON.parse(event.data) as LessonData;
      console.log('[SSE] Received lesson:', lesson.title);
      callbacks.onLesson(lesson, lesson.batch_index || 0);
    } catch (e) {
      console.error('[SSE] Failed to parse lesson data:', e);
    }
  });
  
  // Handle completion event
  eventSource.addEventListener('complete', (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log(`[SSE] Batch complete: ${data.total}/${data.requested} lessons`);
      callbacks.onComplete(data.batch_id, data.total);
      eventSource.close();
    } catch (e) {
      console.error('[SSE] Failed to parse completion data:', e);
    }
  });
  
  // Handle error events
  eventSource.addEventListener('error', (event: any) => {
    // Check if this is a server error with data (not a connection error)
    if (event.data) {
      try {
        const data = JSON.parse(event.data);
        console.error('[SSE] Generation error for topic:', data.topic, data.error);
        callbacks.onError(data.topic, data.error);
      } catch (e) {
        console.error('[SSE] Failed to parse error data:', e);
      }
    } else {
      // Connection/network error - close stream
      console.log('[SSE] Connection closed or error occurred');
      eventSource.close();
    }
  });
  
  // Return cleanup function
  return () => {
    console.log('[SSE] Closing connection');
    eventSource.close();
  };
}

// ========== Quiz API Functions ==========

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  difficulty: string;
  explanation: {
    correct: string;
    incorrect: Record<string, string>;
  };
}

export interface QuizData {
  _id: string;
  topic: string;
  topic_description: string;
  questions: QuizQuestion[];
  metadata: {
    generated_at: string;
    question_count: number;
    topic: string;
    topic_description: string;
  };
  created_at: string;
  user_id?: string;
  lesson_id?: string;
}

export interface QuizResult {
  quiz_id: string;
  attempt_id: string;
  score: number;
  correct_count: number;
  wrong_count: number;
  total_questions: number;
  time_taken_seconds: number;
  passed: boolean;
}

export interface GenerateQuizPayload {
  topic: string;
  topic_description: string;
  lesson_id?: string;
  user_id?: string;
}

export async function generateQuiz(payload: GenerateQuizPayload): Promise<QuizData> {
  try {
    const response = await apiClient.post<QuizData>('/quizzes/generate', payload);
    return response.data;
  } catch (error) {
    console.error('Error generating quiz:', error);
    throw error;
  }
}

export async function getQuiz(quizId: string): Promise<QuizData> {
  try {
    const response = await apiClient.get<QuizData>(`/quizzes/${quizId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching quiz with ID ${quizId}:`, error);
    throw error;
  }
}

export interface SubmitQuizPayload {
  user_id: string;
  quiz_id: string;
  lesson_id?: string;
  answers: Record<string, number>;
  time_taken_seconds: number;
}

export async function submitQuiz(quizId: string, payload: SubmitQuizPayload): Promise<QuizResult> {
  try {
    const response = await apiClient.post<QuizResult>(`/quizzes/${quizId}/submit`, payload);
    return response.data;
  } catch (error) {
    console.error('Error submitting quiz:', error);
    throw error;
  }
}

// ========== Listing API Functions ==========

export interface LessonListItem {
  _id: string;
  topic: string;
  title: string;
  tailored_to_interest?: string;
  duration: number;
  created_at: string;
}

export async function listLessons(skip = 0, limit = 20): Promise<LessonListItem[]> {
  const response = await apiClient.get<LessonListItem[]>('/lessons/', { params: { skip, limit } });
  return response.data;
}

export interface QuizListItem {
  _id: string;
  topic: string;
  topic_description: string;
  question_count: number;
  created_at: string;
}

export async function listQuizzes(skip = 0, limit = 20, userId?: string): Promise<QuizListItem[]> {
  const params: Record<string, any> = { skip, limit };
  if (userId) params.user_id = userId;
  const response = await apiClient.get<QuizListItem[]>('/quizzes/', { params });
  return response.data;
}

export interface QuizAttemptItem {
  _id: string;
  user_id: string;
  quiz_id: string;
  lesson_id?: string;
  answers: Record<string, number>;
  score: number;
  correct_count: number;
  wrong_count: number;
  time_taken_seconds: number;
  completed_at: string;
}

export async function getUserAttempts(userId: string, skip = 0, limit = 50): Promise<QuizAttemptItem[]> {
  const response = await apiClient.get<QuizAttemptItem[]>(`/quizzes/attempts/user/${userId}`, {
    params: { skip, limit },
  });
  return response.data;
}


// ========== Flashcard API Functions ==========

export interface Flashcard {
  _id: string;
  user_id: string;
  topic: string;
  front: string;
  back: string;
  difficulty: 'easy' | 'medium' | 'hard';
  explanation?: string;
  confidence: number;
  ease_factor: number;
  interval: number;
  repetitions: number;
  next_review_date: string;
  last_reviewed?: string;
  created_at: string;
}

export interface FlashcardTopic {
  topic: string;
  count: number;
}

export async function generateFlashcards(topic: string, isCustomTopic: boolean = false): Promise<Flashcard[]> {
  const response = await apiClient.post<Flashcard[]>('/flashcards/generate', {
    topic,
    is_custom_topic: isCustomTopic
  });
  return response.data;
}

export async function getFlashcards(filters?: {
  topic?: string;
  difficulty?: string;
  due_for_review?: boolean;
}): Promise<Flashcard[]> {
  const response = await apiClient.get<Flashcard[]>('/flashcards/', { params: filters });
  return response.data;
}

export async function getFlashcardTopics(): Promise<FlashcardTopic[]> {
  const response = await apiClient.get<FlashcardTopic[]>('/flashcards/topics');
  return response.data;
}

export async function getFlashcard(id: string): Promise<Flashcard> {
  const response = await apiClient.get<Flashcard>(`/flashcards/${id}`);
  return response.data;
}

export async function reviewFlashcard(id: string, confidence: number): Promise<Flashcard> {
  const response = await apiClient.put<Flashcard>(`/flashcards/${id}/review`, { confidence });
  return response.data;
}

export async function updateFlashcard(id: string, updates: {
  front?: string;
  back?: string;
  difficulty?: string;
  explanation?: string;
}): Promise<Flashcard> {
  const response = await apiClient.put<Flashcard>(`/flashcards/${id}`, updates);
  return response.data;
}

export async function deleteFlashcard(id: string): Promise<void> {
  await apiClient.delete(`/flashcards/${id}`);
}

