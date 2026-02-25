// frontend/src/app/lesson/page.tsx
'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useLessonStore } from '@/src/store/lessonStore';
import { fetchTestLesson, fetchLesson, LessonData, fetchWordTimestamps } from '@/src/services/api'; // Added fetchWordTimestamps
import LessonCanvas from '@/src/components/LessonCanvas';
import AudioController from '@/src/components/AudioController';

const LessonPlayer: React.FC = () => {
  const { lessonData, setLessonData, resetPlayback } = useLessonStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const searchParams = useSearchParams();
  const lessonId = searchParams.get('id');

  useEffect(() => {
    const loadLesson = async () => {
      try {
        setLoading(true);
        setError(null);

        let data: LessonData;
        if (lessonId) {
          data = await fetchLesson(lessonId);
        } else {
          data = await fetchTestLesson();
        }
        setLessonData(data);

        // Fetch timestamps and synced board actions if lesson has an ID
        if (data._id) {
          try {
            const timestampData = await fetchWordTimestamps(data._id);
            if (timestampData.board_actions_synced) {
              // Merge synced board actions into lesson data
              setLessonData({
                ...data,
                board_actions_synced: timestampData.board_actions_synced,
              } as any);
            }
          } catch (timestampError) {
            console.warn('Failed to load timestamps, using original timing:', timestampError);
            // Not critical - lesson can still play with original timestamps
          }
        }
      } catch (err) {
        setError('Failed to load lesson. Please try again.');
        console.error('Error loading lesson:', err);
      } finally {
        setLoading(false);
      }
    };

    loadLesson();

    return () => {
      resetPlayback();
    };
  }, [lessonId, setLessonData, resetPlayback]);

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
    <div className="max-w-7xl mx-auto p-8 flex space-x-8"> {/* Adjusted container and added flex for side-by-side */}
      {/* Left side: Lesson Player */}
      <div className="flex-1"> {/* Takes up available space */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {lessonData.title}
          </h1>
          <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            {lessonData.topic}
          </span>
        </div>

        <div className="mb-6">
          <LessonCanvas />
        </div>

        <div>
          <AudioController />
        </div>
      </div>

      {/* Right side: Raw LLM Response */}
      {lessonData.raw_llm_output && (
        <div className="flex-1 bg-gray-50 p-6 rounded-lg shadow-inner max-h-[80vh] overflow-auto">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Raw LLM Response (for Debugging)</h2>
          <pre className="whitespace-pre-wrap text-sm font-mono bg-gray-100 p-4 rounded-md overflow-x-auto">
            {JSON.stringify(lessonData.raw_llm_output, null, 2)}
          </pre>
        </div>
      )}
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