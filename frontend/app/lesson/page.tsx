// frontend/src/app/lesson/page.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation'; // NEW IMPORT
import { useLessonStore } from '@/src/store/lessonStore';
import { fetchTestLesson, fetchLesson } from '@/src/services/api'; // UPDATED IMPORT
import LessonCanvas from '@/src/components/LessonCanvas';
import AudioController from '@/src/components/AudioController';

const LessonPlayer: React.FC = () => {
  const { lessonData, setLessonData, resetPlayback } = useLessonStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const searchParams = useSearchParams(); // NEW: Get search params
  const lessonId = searchParams.get('id'); // NEW: Get lesson ID from URL

  useEffect(() => {
    const loadLesson = async () => {
      try {
        setLoading(true);
        setError(null);

        let data;
        if (lessonId) {
          // If lessonId exists, fetch the specific lesson
          data = await fetchLesson(lessonId); // Use the new fetchLesson function
        } else {
          // Otherwise, fall back to the test lesson
          data = await fetchTestLesson();
        }
        setLessonData(data);
      } catch (err) {
        setError('Failed to load lesson. Please try again.');
        console.error('Error loading lesson:', err);
      } finally {
        setLoading(false);
      }
    };

    loadLesson();

    // Cleanup on unmount
    return () => {
      resetPlayback();
    };
  }, [lessonId, setLessonData, resetPlayback]); // Add lessonId to dependencies

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <p className="text-lg text-gray-600">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-lg text-red-600 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!lessonData) {
    return null;
  }

  return (
    <div className="max-w-6xl mx-auto p-8">
      {/* Title Section */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {lessonData.title}
        </h1>
        <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
          {lessonData.topic}
        </span>
      </div>

      {/* Lesson Canvas */}
      <div className="mb-6">
        <LessonCanvas />
      </div>

      {/* Audio Controller */}
      <div>
        <AudioController />
      </div>
    </div>
  );
};

export default LessonPlayer;