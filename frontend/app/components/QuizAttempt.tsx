'use client'

import React, { useEffect, useState } from 'react'

const QUESTIONS = [
  {
    question: 'What is the capital of France?',
    options: ['Berlin', 'Madrid', 'Paris', 'Rome'],
  },
  {
    question: 'Which planet is known as the Red Planet?',
    options: ['Earth', 'Mars', 'Jupiter', 'Venus'],
  },
  {
    question: 'Who developed the theory of relativity?',
    options: ['Newton', 'Einstein', 'Tesla', 'Galileo'],
  },
  // add up to 10 questions
]

const TOTAL_TIME = 120 * QUESTIONS.length // 20 mins for 10 questions


export default function QuizAttempt({ onEnd }: { onEnd: () => void }) {
  const [current, setCurrent] = useState(0)
  const [timeLeft, setTimeLeft] = useState(TOTAL_TIME)

  const [answers, setAnswers] = useState<(number | null)[]>(
    Array(QUESTIONS.length).fill(null)
  )

  // timer logic
  useEffect(() => {
    setTimeLeft(TOTAL_TIME)

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev === 1) {
          clearInterval(timer)
          handleNext()
          return TOTAL_TIME
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [current])

  const handleOptionSelect = (index: number) => {
    const updated = [...answers]
    updated[current] = index
    setAnswers(updated)
  }

  const handleNext = () => {
    if (current < QUESTIONS.length - 1) {
      setCurrent(current + 1)
    }
  }

  const handlePrev = () => {
    if (current > 0) {
      setCurrent(current - 1)
    }
  }

  return (
    <div className="p-6 max-w-4xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Question {current + 1} / {QUESTIONS.length}
        </h2>

        <div className="text-sm font-medium text-gray-700">
          ⏱ {Math.floor(timeLeft / 60)}:
          {(timeLeft % 60).toString().padStart(2, '0')}
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {QUESTIONS[current].question}
        </h3>

        <div className="space-y-3">
          {QUESTIONS[current].options.map((opt, index) => (
            <button
              key={index}
              onClick={() => handleOptionSelect(index)}
              className={`w-full text-left px-4 py-3 rounded-lg border transition
                ${
                  answers[current] === index
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:bg-gray-50'
                }
              `}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center mt-6">
        <button
          onClick={handlePrev}
          disabled={current === 0}
          className="px-4 py-2 rounded-lg border border-gray-300 disabled:opacity-50"
        >
          Previous
        </button>

        <div className="space-x-3">
          <button
            onClick={onEnd}
            className="px-4 py-2 rounded-lg border border-red-300 text-red-600 hover:bg-red-50"
          >
            End Quiz
          </button>

          <button
            onClick={handleNext}
            disabled={current === QUESTIONS.length - 1}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
