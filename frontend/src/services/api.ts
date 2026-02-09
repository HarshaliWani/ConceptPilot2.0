// frontend/src/services/api.ts
import axios from 'axios';

const baseURL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL,
  timeout: 200000, // Increased to 200 seconds for lesson generation + TTS
});


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
}


// Fetch a test lesson (if needed)
export async function fetchTestLesson(): Promise<LessonData> {
  try {
    const response = await apiClient.get<LessonData>('/lessons/svg-test-lesson');
    return response.data;
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