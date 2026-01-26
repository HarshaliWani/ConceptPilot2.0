import { create } from 'zustand';

interface LessonState {
  lessonData: any | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  audioElement: HTMLAudioElement | null;
}

interface LessonActions {
  setLessonData: (data: any) => void;
  setIsPlaying: (playing: boolean) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setAudioElement: (audio: HTMLAudioElement) => void;
  resetPlayback: () => void;
}

type LessonStore = LessonState & LessonActions;

export const useLessonStore = create<LessonStore>((set) => ({
  // Initial state
  lessonData: null,
  isPlaying: false,
  currentTime: 0,
  duration: 0,
  audioElement: null,

  // Actions
  setLessonData: (data: any) => set({ lessonData: data }),
  setIsPlaying: (playing: boolean) => set({ isPlaying: playing }),
  setCurrentTime: (time: number) => set({ currentTime: time }),
  setDuration: (duration: number) => set({ duration: duration }),
  setAudioElement: (audio: HTMLAudioElement) => set({ audioElement: audio }),
  resetPlayback: () => set({
    lessonData: null,
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    audioElement: null,
  }),
}));

