'use client';

import React from 'react';
import { QuizQuestion } from '../services/api';

interface QuizCardProps {
  question: QuizQuestion;
  questionNumber: number;
  selectedAnswer: number | null;
  onAnswerSelect: (answerIndex: number) => void;
  showResults: boolean;
  disabled?: boolean;
}

const QuizCard: React.FC<QuizCardProps> = ({
  question,
  questionNumber,
  selectedAnswer,
  onAnswerSelect,
  showResults,
  disabled = false,
}) => {
  const getOptionClass = (optionIndex: number) => {
    const baseClass = 'p-4 rounded-lg border cursor-pointer transition-all duration-200';
    
    if (!showResults) {
      // Normal mode - show selection
      if (selectedAnswer === optionIndex) {
        return `${baseClass} border-blue-500 bg-blue-50`;
      }
      return `${baseClass} border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300`;
    } else {
      // Review mode - show correct/incorrect
      if (optionIndex === question.correctAnswer) {
        return `${baseClass} border-green-500 bg-green-50`;
      } else if (selectedAnswer === optionIndex) {
        return `${baseClass} border-red-500 bg-red-50`;
      }
      return `${baseClass} border-gray-200 bg-gray-50`;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Question Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-gray-500">
          Question {questionNumber}
        </span>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(question.difficulty)}`}>
          {question.difficulty}
        </span>
      </div>

      {/* Question Text */}
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        {question.question}
      </h3>

      {/* Options */}
      <div className="space-y-3">
        {question.options.map((option, index) => (
          <div key={index}>
            <div
              className={getOptionClass(index)}
              onClick={() => !disabled && !showResults && onAnswerSelect(index)}
            >
              <div className="flex items-center">
                <div className={`h-5 w-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                  selectedAnswer === index ? 'border-blue-500' : 'border-gray-300'
                }`}>
                  {selectedAnswer === index && (
                    <div className="h-3 w-3 rounded-full bg-blue-500"></div>
                  )}
                  {showResults && index === question.correctAnswer && (
                    <div className="h-3 w-3 rounded-full bg-green-500"></div>
                  )}
                </div>
              <span className="text-zinc-800">{option}</span>
              </div>
            </div>

            {/* Show explanation in review mode */}
            {showResults && (
              <div className="mt-2 ml-8 p-3 bg-gray-50 rounded border border-gray-200 text-sm text-gray-700">
                {index === question.correctAnswer ? (
                  <div>
                    <span className="font-medium text-green-600">✓ Correct: </span>
                    {question.explanation.correct}
                  </div>
                ) : (
                  <div>
                    <span className="font-medium text-gray-600">Why incorrect: </span>
                    {question.explanation.incorrect[index.toString()]}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuizCard;
