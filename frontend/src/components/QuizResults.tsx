'use client';

import React from 'react';
import { QuizResult } from '../services/api';

interface QuizResultsProps {
  result: QuizResult;
  onReviewAnswers: () => void;
  onReturnToDashboard: () => void;
}

const QuizResults: React.FC<QuizResultsProps> = ({
  result,
  onReviewAnswers,
  onReturnToDashboard,
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-zinc-600';
    return 'text-zinc-700';
  };

  const getScoreMessage = (score: number) => {
    if (score >= 90) return 'Excellent! Outstanding performance! 🎉';
    if (score >= 70) return 'Great job! You passed! ✓';
    if (score >= 50) return 'Not bad, but you can do better! 💪';
    return 'Keep practicing! Review the material and try again. 📚';
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg border border-zinc-200 p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="mb-4">
          {result.passed ? (
            <div className="mx-auto w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center">
              <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          ) : (
            <div className="mx-auto w-20 h-20 rounded-full bg-zinc-100 flex items-center justify-center">
              <svg className="w-12 h-12 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          )}
        </div>
        <h2 className="text-3xl font-bold text-zinc-900 mb-2">Quiz Complete!</h2>
        <p className="text-zinc-600">{getScoreMessage(result.score)}</p>
      </div>

      {/* Score Display */}
      <div className="mb-8">
        <div className="text-center mb-6">
          <div className={`text-6xl font-bold ${getScoreColor(result.score)}`}>
            {result.score.toFixed(1)}%
          </div>
          <p className="text-gray-500 mt-2">Your Score</p>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-zinc-200 rounded-full h-3 mb-6">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              result.passed ? 'bg-blue-500' : 'bg-zinc-400'
            }`}
            style={{ width: `${result.score}%` }}
          ></div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg text-center border border-blue-100">
            <div className="text-2xl font-bold text-blue-600">{result.correct_count}</div>
            <div className="text-sm text-zinc-600">Correct</div>
          </div>
          <div className="bg-zinc-100 p-4 rounded-lg text-center border border-zinc-200">
            <div className="text-2xl font-bold text-zinc-700">{result.wrong_count}</div>
            <div className="text-sm text-zinc-600">Wrong</div>
          </div>
          <div className="bg-zinc-50 p-4 rounded-lg text-center border border-zinc-200">
            <div className="text-2xl font-bold text-zinc-700">{result.total_questions}</div>
            <div className="text-sm text-zinc-600">Total</div>
          </div>
        </div>

        {/* Time Taken */}
        <div className="bg-zinc-50 p-4 rounded-lg border border-zinc-200">
          <div className="flex items-center justify-between">
            <span className="text-zinc-700 font-medium">Time Taken</span>
            <span className="text-zinc-900 font-bold">
              {Math.floor(result.time_taken_seconds / 60)}m {result.time_taken_seconds % 60}s
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={onReviewAnswers}
          className="flex-1 py-3 px-6 border-2 border-blue-500 text-blue-500 rounded-lg font-medium hover:bg-blue-50 transition-colors"
        >
          Review Answers
        </button>
        <button
          onClick={onReturnToDashboard}
          className="flex-1 py-3 px-6 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
        >
          Continue Learning
        </button>
      </div>

      {/* Passing Criteria */}
      <div className="mt-6 text-center text-sm text-zinc-500">
        Passing score: 70% or higher
      </div>
    </div>
  );
};

export default QuizResults;
