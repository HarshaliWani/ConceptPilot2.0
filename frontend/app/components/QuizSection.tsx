'use client'

import React, { useState, useEffect } from 'react'
import { CheckCircle, XCircle, RotateCcw } from 'lucide-react'

interface Quiz {
  question: string
  options: string[]
  correct: number
  explanation: string
}

interface QuizSectionProps {
  quiz: Quiz | null
}

const QuizSection: React.FC<QuizSectionProps> = ({ quiz }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [hasAnswered, setHasAnswered] = useState(false)

  useEffect(() => {
    if (quiz) {
      setSelectedAnswer(null)
      setShowResult(false)
      setHasAnswered(false)
    }
  }, [quiz])

  const handleSubmit = () => {
    if (selectedAnswer !== null) {
      setShowResult(true)
      setHasAnswered(true)
    }
  }

  const handleReset = () => {
    setSelectedAnswer(null)
    setShowResult(false)
    setHasAnswered(false)
  }

  if (!quiz) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center h-full flex items-center justify-center">
        <div>
          <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready for a Quiz?</h3>
          <p className="text-gray-600">Ask the AI tutor a question to generate a personalized quiz!</p>
        </div>
      </div>
    )
  }

  const isCorrect = selectedAnswer === quiz.correct

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 h-full overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Quick Quiz</h3>
        {hasAnswered && (
          <button
            onClick={handleReset}
            className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Try Again</span>
          </button>
        )}
      </div>

      <div className="space-y-6">
        <div>
          <h4 className="text-base font-medium text-gray-900 mb-4">{quiz.question}</h4>
          
          <div className="space-y-3">
            {quiz.options.map((option, index) => (
              <label
                key={index}
                className={`flex items-center space-x-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedAnswer === index
                    ? showResult
                      ? index === quiz.correct
                        ? 'border-green-500 bg-green-50'
                        : 'border-red-500 bg-red-50'
                      : 'border-blue-500 bg-blue-50'
                    : showResult && index === quiz.correct
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                } ${hasAnswered ? 'cursor-default' : 'cursor-pointer'}`}
              >
                <input
                  type="radio"
                  name="quiz-option"
                  value={index}
                  checked={selectedAnswer === index}
                  onChange={() => !hasAnswered && setSelectedAnswer(index)}
                  disabled={hasAnswered}
                  className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                />
                <span className={`flex-1 ${
                  showResult && selectedAnswer === index
                    ? index === quiz.correct
                      ? 'text-green-800 font-medium'
                      : 'text-red-800 font-medium'
                    : showResult && index === quiz.correct
                    ? 'text-green-800 font-medium'
                    : 'text-gray-900'
                }`}>
                  {option}
                </span>
                
                {showResult && index === quiz.correct && (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                )}
                {showResult && selectedAnswer === index && index !== quiz.correct && (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
              </label>
            ))}
          </div>
        </div>

        {!showResult ? (
          <button
            onClick={handleSubmit}
            disabled={selectedAnswer === null}
            className="w-full py-3 px-6 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Submit Answer
          </button>
        ) : (
          <div className={`p-4 rounded-lg ${
            isCorrect ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              {isCorrect ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600" />
              )}
              <span className={`font-medium ${
                isCorrect ? 'text-green-800' : 'text-red-800'
              }`}>
                {isCorrect ? 'Correct!' : 'Not quite right.'}
              </span>
            </div>
            <p className={`text-sm ${
              isCorrect ? 'text-green-700' : 'text-red-700'
            }`}>
              {quiz.explanation}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default QuizSection