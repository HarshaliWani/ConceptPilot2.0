'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { generateLesson } from '@/src/services/api';

const GenerateLesson: React.FC = () => {
  const router = useRouter();
  const [topic, setTopic] = useState('');
  const [userInterest, setUserInterest] = useState('');
  const [proficiencyLevel, setProficiencyLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('beginner');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const lesson = await generateLesson({
        topic,
        user_interest: userInterest,
        proficiency_level: proficiencyLevel,
      });
      // Redirect to the lesson page with the generated lesson ID
      router.push(`/lesson?id=${lesson._id}`);
    } catch (err: any) {
      console.error('Error generating lesson:', err);
      setError(err?.response?.data?.error || 'Failed to generate lesson. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-8 bg-white shadow-lg rounded-lg mt-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">Generate New Lesson</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">
            Lesson Topic:
          </label>
          <input
            type="text"
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Photosynthesis, Quantum Physics"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="userInterest" className="block text-sm font-medium text-gray-700 mb-1">
            User Interest:
          </label>
          <input
            type="text"
            id="userInterest"
            value={userInterest}
            onChange={(e) => setUserInterest(e.target.value)}
            placeholder="e.g., Elden Ring, Basketball, Cooking"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="proficiencyLevel" className="block text-sm font-medium text-gray-700 mb-1">
            Proficiency Level:
          </label>
          <select
            id="proficiencyLevel"
            value={proficiencyLevel}
            onChange={(e) => setProficiencyLevel(e.target.value as 'beginner' | 'intermediate' | 'advanced')}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        {error && (
          <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white px-6 py-3 rounded-md text-lg font-semibold hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating lesson...
            </>
          ) : (
            'Generate Lesson'
          )}
        </button>
      </form>
    </div>
  );
};

export default GenerateLesson;