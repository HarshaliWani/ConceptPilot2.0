// frontend/src/components/AudioController.tsx
import React, { useEffect, useRef } from 'react';
import { useLessonStore } from '../store/lessonStore';

const AudioController: React.FC = () => {
  const { lessonData, isPlaying, currentTime, duration, setCurrentTime, setDuration, setIsPlaying } = useLessonStore();
  const audioRef = useRef<HTMLAudioElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Refs to hold the latest state values for the interval callback
  const currentTimeRef = useRef(currentTime);
  const isPlayingRef = useRef(isPlaying);

  // Update refs whenever currentTime or isPlaying changes
  useEffect(() => {
    currentTimeRef.current = currentTime;
  }, [currentTime]);

  useEffect(() => {
    isPlayingRef.current = isPlaying;
  }, [isPlaying]);

  // Handle play/pause for actual audio element (if audio_url exists)
  useEffect(() => {
    if (isPlaying) {
      audioRef.current?.play();
    } else {
      audioRef.current?.pause();
    }
  }, [isPlaying]);

  // Set up event listeners for actual audio element
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      // Ensure current time is set to duration when playback ends
      setCurrentTime(audio.duration);
    };

    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [setDuration, setCurrentTime, setIsPlaying]);

  // Mock audio playback simulation when audio_url is null
  useEffect(() => {
    if (!lessonData || lessonData.audio_url) {
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
  }, [isPlaying, lessonData, duration, setCurrentTime, setIsPlaying]); // currentTime is removed from dependencies here

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
    <div className="flex gap-4 items-center p-4 bg-gray-100 rounded">
      {/* Hidden audio element */}
      {lessonData?.audio_url && (
        <audio ref={audioRef} src={lessonData.audio_url} />
      )}

      {/* Play/Pause Button */}
      {!isPlaying ? (
        <button
          onClick={handlePlay}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Play
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
        value={isNaN(currentTime) ? 0 : currentTime}
        onChange={handleSeek}
        className="flex-1"
      />
    </div>
  );
};

export default AudioController;