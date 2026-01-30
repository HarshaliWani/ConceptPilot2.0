// frontend/src/services/api.ts
import axios from 'axios';

const baseURL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL,
  timeout: 10000,
});

export interface LessonData {
  id: string;
  topic: string;
  title: string;
  narration_script: string;
  board_actions: Array<{ timestamp: number; type: string; [key: string]: any }>;
  audio_url: string | null;
  duration: number;
  created_at: string;
  tailored_to_interest: string;
  raw_llm_output: string;
}

export async function fetchTestLesson(): Promise<LessonData> {
  try {
    const response = await apiClient.get<LessonData>('/lessons/svg-test-lesson/');
    return response.data;
  } catch (error) {
    console.error('Error fetching test lesson:', error);
    throw error;
  }
}

export async function fetchLesson(lessonId: string): Promise<LessonData> {
  try {
    const response = await apiClient.get<LessonData>(`/lessons/${lessonId}/`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching lesson with ID ${lessonId}:`, error);
    throw error;
  }
}