import { create } from 'zustand';

interface WordTimestamp {
  word: string;
  start: number;
  end: number;
}

interface LessonState {
  lessonData: any | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  audioElement: HTMLAudioElement | null;
  wordTimestamps: WordTimestamp[];
  isLoadingTimestamps: boolean;
  currentWord: WordTimestamp | null;
  useStreamingAudio: boolean;
  // Playlist support
  lessonPlaylist: any[];
  currentLessonIndex: number;
  batchId: string | null;
}

interface LessonActions {
  setLessonData: (data: any) => void;
  setIsPlaying: (playing: boolean) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setAudioElement: (audio: HTMLAudioElement) => void;
  setWordTimestamps: (timestamps: WordTimestamp[]) => void;
  setIsLoadingTimestamps: (loading: boolean) => void;
  setCurrentWord: (word: WordTimestamp | null) => void;
  setUseStreamingAudio: (useStreaming: boolean) => void;
  // Playlist actions
  setLessonPlaylist: (playlist: any[], batchId: string | null) => void;
  setCurrentLessonIndex: (index: number) => void;
  playNextLesson: () => void;
  resetPlayback: () => void;
}

type LessonStore = LessonState & LessonActions;

export const useLessonStore = create<LessonStore>((set, get) => ({
  // Initial state
  lessonData: null,
  isPlaying: false,
  currentTime: 0,
  duration: 0,
  audioElement: null,
  wordTimestamps: [],
  isLoadingTimestamps: false,
  currentWord: null,
  useStreamingAudio: true, // Enable streaming by default
  lessonPlaylist: [],
  currentLessonIndex: 0,
  batchId: null,

  // Actions
  setLessonData: (data: any) => set({ lessonData: data }),
  setIsPlaying: (playing: boolean) => set({ isPlaying: playing }),
  setCurrentTime: (time: number) => set({ currentTime: time }),
  setDuration: (duration: number) => set({ duration: duration }),
  setAudioElement: (audio: HTMLAudioElement) => set({ audioElement: audio }),
  setWordTimestamps: (timestamps: WordTimestamp[]) => set({ wordTimestamps: timestamps }),
  setIsLoadingTimestamps: (loading: boolean) => set({ isLoadingTimestamps: loading }),
  setCurrentWord: (word: WordTimestamp | null) => set({ currentWord: word }),
  setUseStreamingAudio: (useStreaming: boolean) => set({ useStreamingAudio: useStreaming }),
  
  // Playlist actions
  setLessonPlaylist: (playlist: any[], batchId: string | null) => {
    if (playlist.length > 0) {
      set({
        lessonPlaylist: playlist,
        batchId: batchId,
        currentLessonIndex: 0,
        lessonData: playlist[0],
        currentTime: 0,
        isPlaying: false,
        wordTimestamps: [],
      });
    }
  },
  
  setCurrentLessonIndex: (index: number) => {
    const { lessonPlaylist } = get();
    if (index >= 0 && index < lessonPlaylist.length) {
      set({
        currentLessonIndex: index,
        lessonData: lessonPlaylist[index],
        currentTime: 0,
        isPlaying: false,
        wordTimestamps: [],
      });
    }
  },
  
  playNextLesson: () => {
    const { currentLessonIndex, lessonPlaylist } = get();
    if (currentLessonIndex < lessonPlaylist.length - 1) {
      const nextIndex = currentLessonIndex + 1;
      set({
        currentLessonIndex: nextIndex,
        lessonData: lessonPlaylist[nextIndex],
        currentTime: 0,
        isPlaying: false, // Will be set to true by caller
        wordTimestamps: [],
      });
      return true; // Has next lesson
    }
    return false; // No more lessons
  },
  
  resetPlayback: () => set({
    lessonData: null,
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    audioElement: null,
    wordTimestamps: [],
    isLoadingTimestamps: false,
    currentWord: null,
    lessonPlaylist: [],
    currentLessonIndex: 0,
    batchId: null,
  }),
}));
