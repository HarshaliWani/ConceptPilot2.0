// frontend/src/components/AudioController.tsx
import React, { useEffect, useRef, useMemo, useState } from 'react';
import { useLessonStore } from '../store/lessonStore';
import { getStreamingAudioUrl, fetchWordTimestamps } from '../services/api';

const BACKEND_URL = 'http://localhost:8000';

interface PlaylistChunk {
  index: number;
  file: string;
  duration: number;
  start_time: number;
}

interface PlaylistData {
  lesson_id: string;
  total_duration: number;
  chunk_count: number;
  pause_duration: number;
  chunks: PlaylistChunk[];
}

const AudioController: React.FC = () => {
  const { 
    lessonData, 
    isPlaying, 
    currentTime, 
    duration, 
    wordTimestamps,
    currentWord,
    useStreamingAudio,
    lessonPlaylist,
    currentLessonIndex,
    setCurrentTime, 
    setDuration, 
    setIsPlaying,
    setCurrentWord,
    setWordTimestamps,
    playNextLesson 
  } = useLessonStore();
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Playlist support
  const [playlist, setPlaylist] = useState<PlaylistData | null>(null);
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [isLoadingPlaylist, setIsLoadingPlaylist] = useState(false);

  // Refs to hold the latest state values for the interval callback
  const currentTimeRef = useRef(currentTime);
  const isPlayingRef = useRef(isPlaying);
  
  // Detect if audio_url is a playlist and load it
  useEffect(() => {
    if (!lessonData?.audio_url) {
      setPlaylist(null);
      return;
    }
    
    // Check if it's a playlist JSON file
    if (lessonData.audio_url.includes('_playlist.json')) {
      setIsLoadingPlaylist(true);
      const playlistUrl = lessonData.audio_url.startsWith('http') 
        ? lessonData.audio_url 
        : `${BACKEND_URL}${lessonData.audio_url}`;
      
      fetch(playlistUrl)
        .then(res => res.json())
        .then((data: PlaylistData) => {
          setPlaylist(data);
          setDuration(data.total_duration);
          setCurrentChunkIndex(0);
          console.log(`[AudioController] Loaded playlist with ${data.chunk_count} chunks, total duration: ${data.total_duration}s`);
        })
        .catch(err => {
          console.error('[AudioController] Failed to load playlist:', err);
          setPlaylist(null);
        })
        .finally(() => setIsLoadingPlaylist(false));
    } else {
      setPlaylist(null);
    }
  }, [lessonData?.audio_url, setDuration]);

  // Resolve the audio URL - handle playlist or single audio
  const audioSrc = useMemo(() => {
    if (!lessonData?.audio_url) return null;
    
    // If we have a playlist, use the current chunk's audio
    if (playlist && playlist.chunks[currentChunkIndex]) {
      const chunkFile = playlist.chunks[currentChunkIndex].file;
      return chunkFile.startsWith('http') ? chunkFile : `${BACKEND_URL}${chunkFile}`;
    }
    
    // If it's a playlist but still loading, wait
    if (lessonData.audio_url.includes('_playlist.json') && !playlist) {
      return null;
    }
    
    // If streaming is enabled and we have a lesson ID, use streaming endpoint
    if (useStreamingAudio && lessonData._id && !lessonData.audio_url.includes('_playlist.json')) {
      return getStreamingAudioUrl(lessonData._id);
    }
    
    // Otherwise, use static audio file
    if (lessonData.audio_url.startsWith('http')) return lessonData.audio_url;
    return `${BACKEND_URL}${lessonData.audio_url}`;
  }, [lessonData?.audio_url, lessonData?._id, useStreamingAudio, playlist, currentChunkIndex]);

  // Fetch word timestamps when lesson loads
  useEffect(() => {
    if (!lessonData?._id || wordTimestamps.length > 0) return;

    fetchWordTimestamps(lessonData._id)
      .then((data) => {
        if (data.word_timestamps) {
          setWordTimestamps(data.word_timestamps);
        }
      })
      .catch((error) => {
        console.error('Failed to fetch word timestamps:', error);
      });
  }, [lessonData?._id, wordTimestamps.length, setWordTimestamps]);

  // Update refs whenever currentTime or isPlaying changes
  useEffect(() => {
    currentTimeRef.current = currentTime;
  }, [currentTime]);

  useEffect(() => {
    isPlayingRef.current = isPlaying;
  }, [isPlaying]);

  // Update current word based on timestamps
  useEffect(() => {
    if (!wordTimestamps.length) {
      setCurrentWord(null);
      return;
    }

    // Find the word that matches the current time
    const word = wordTimestamps.find(
      (w) => w.start <= currentTime && w.end >= currentTime
    );
    
    setCurrentWord(word || null);
  }, [currentTime, wordTimestamps, setCurrentWord]);

  // Handle play/pause for actual audio element (if audio_url exists)
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      // Play returns a promise, handle potential AbortError
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch(error => {
          // Ignore AbortError (happens when play interrupted by pause)
          if (error.name !== 'AbortError') {
            console.error('[Audio] Play error:', error);
          }
        });
      }
    } else {
      audio.pause();
    }
  }, [isPlaying]);

  // Set up event listeners for actual audio element
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      // For playlist, don't override duration with chunk duration
      if (!playlist) {
        setDuration(audio.duration);
      }
    };

    const handleTimeUpdate = () => {
      // For playlist, adjust currentTime relative to full timeline
      if (playlist && playlist.chunks[currentChunkIndex]) {
        const chunkStartTime = playlist.chunks[currentChunkIndex].start_time;
        setCurrentTime(chunkStartTime + audio.currentTime);
      } else {
        setCurrentTime(audio.currentTime);
      }
    };

    const handleEnded = () => {
      // If playlist and more chunks remain, play next chunk after pause
      if (playlist && currentChunkIndex < playlist.chunks.length - 1) {
        console.log(`[AudioController] Chunk ${currentChunkIndex + 1} ended, playing next chunk after pause...`);
        setIsPlaying(false);
        
        // Brief pause before next chunk (pause_duration is in seconds)
        setTimeout(() => {
          setCurrentChunkIndex(prev => prev + 1);
          // Audio will auto-play when new chunk loads due to isPlaying state
          setTimeout(() => setIsPlaying(true), 100);
        }, (playlist.pause_duration || 0.7) * 1000);
      } else {
        // All chunks complete - check if we're in a lesson playlist
        const hasNextLesson = lessonPlaylist.length > 0 && playNextLesson();
        
        if (hasNextLesson) {
          console.log(`[AudioController] Lesson ${currentLessonIndex + 1} complete, auto-advancing to next lesson...`);
          setIsPlaying(false);
          setCurrentChunkIndex(0); // Reset chunk index for new lesson
          
          // Brief pause before next lesson
          setTimeout(() => {
            setIsPlaying(true);
          }, 1500); // 1.5s pause between lessons
        } else {
          // No more lessons - stop playback
          setIsPlaying(false);
          setCurrentTime(duration);
          
          if (lessonPlaylist.length > 0) {
            console.log('[AudioController] Playlist complete! All lessons finished.');
          }
        }
      }
    };

    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [setDuration, setCurrentTime, setIsPlaying, playlist, currentChunkIndex, duration, lessonPlaylist, currentLessonIndex, playNextLesson]);

  // Mock audio playback simulation when audio_url is null
  useEffect(() => {
    if (!lessonData || audioSrc) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // This effect handles starting/stopping the interval.
    // It should not depend on currentTime itself to avoid re-running frequently.
    if (isPlaying) {
      // Clear any existing interval before starting a new one
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }

      intervalRef.current = setInterval(() => {
        // Use the ref to get the latest currentTime
        const newTime = currentTimeRef.current + 0.1;
        if (newTime >= duration) {
          setIsPlaying(false);
          setCurrentTime(duration); // Set to duration if it ends
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        } else {
          setCurrentTime(newTime); // Update the store with the new time
        }
      }, 100);
    } else {
      // If not playing, ensure the interval is cleared
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      // Cleanup interval on unmount or when dependencies change (e.g., audio_url becomes available)
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, lessonData, audioSrc, duration, setCurrentTime, setIsPlaying]); // currentTime is removed from dependencies here

  // Initialize duration from lessonData (only if not already set)
  useEffect(() => {
    if (lessonData && lessonData.duration && duration === 0) {
      setDuration(lessonData.duration);
    }
  }, [lessonData, duration, setDuration]);

  const handlePlay = () => {
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const formatTime = (seconds: number): string => {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col gap-2">
      {/* Playlist indicator */}
      {playlist && (
        <div className="text-xs text-gray-600 px-4">
          📻 Multi-part lesson: Playing segment {currentChunkIndex + 1} of {playlist.chunk_count}
        </div>
      )}
      
      <div className="flex gap-4 items-center p-4 bg-gray-100 rounded">
        {/* Hidden audio element */}
        {audioSrc && (
          <audio ref={audioRef} src={audioSrc} preload="auto" />
        )}

        {/* Play/Pause Button */}
        {!isPlaying ? (
          <button
            onClick={handlePlay}
            disabled={isLoadingPlaylist}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {isLoadingPlaylist ? 'Loading...' : 'Play'}
          </button>
        ) : (
          <button
            onClick={handlePause}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Pause
          </button>
        )}

        {/* Time Display */}
        <span className="text-sm font-mono">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>

        {/* Seek Bar */}
        <input
          type="range"
          min={0}
          max={isNaN(duration) ? 0 : duration}
          step={0.1}
          value={isNaN(currentTime) ? 0 : currentTime}
          onChange={handleSeek}
          className="flex-1 cursor-pointer"
        />
      </div>
    </div>
  );
};

export default AudioController;