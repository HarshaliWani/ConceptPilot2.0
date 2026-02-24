// frontend/src/app/lesson/page.tsx
'use client';

import React, { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation'; // NEW IMPORT
import { useLessonStore } from '@/src/store/lessonStore';
import { fetchTestLesson, fetchLesson, LessonData, generateQuiz } from '@/src/services/api';
import LessonCanvas from '@/src/components/LessonCanvas';
import AudioController from '@/src/components/AudioController';

const LessonPlayer: React.FC = () => {
  const { lessonData, setLessonData, resetPlayback, currentTime, duration } = useLessonStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generatingQuiz, setGeneratingQuiz] = useState(false);

  const router = useRouter();
  const searchParams = useSearchParams(); // NEW: Get search params
  const lessonId = searchParams.get('id'); // NEW: Get lesson ID from URL

  const isLessonCompleted = duration > 0 && currentTime >= duration * 0.95; // 95% completion

  const handleTakeQuiz = async () => {
    if (!lessonData) return;

    setGeneratingQuiz(true);
    try {
      const quiz = await generateQuiz({
        topic: lessonData.topic,
        topic_description: lessonData.title,
        lesson_id: lessonId || undefined,
        user_id: 'user123' // TODO: Get userId from auth
      });
      router.push(`/quiz?id=${quiz._id}`);
    } catch (err) {
      console.error('Failed to generate quiz:', err);
      alert('Failed to generate quiz. Please try again.');
    } finally {
      setGeneratingQuiz(false);
    }
  };

  useEffect(() => {
    const loadLesson = async () => {
      try {
        setLoading(true);
        setError(null);

        let data: LessonData;
        if (lessonId) {
          // If lessonId exists, fetch the specific lesson
          data = await fetchLesson(lessonId);
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

      {/* Quiz Section */}
      <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Test Your Knowledge
            </h3>
            <p className="text-gray-600">
              {isLessonCompleted 
                ? '🎉 Great! You\'ve completed the lesson. Ready to test your understanding?' 
                : '📚 Take a quiz to reinforce your learning'}
            </p>
          </div>
          <button
            onClick={handleTakeQuiz}
            disabled={generatingQuiz}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              generatingQuiz
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 text-white shadow-md hover:shadow-lg'
            }`}
          >
            {generatingQuiz ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating...
              </span>
            ) : (
              '📝 Take Quiz'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default function LessonPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading lesson...</div>}>
      <LessonPlayer />
    </Suspense>
  );
}