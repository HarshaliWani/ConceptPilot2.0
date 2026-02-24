

'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Brain, Clock, CheckCircle, Play, Loader2 } from 'lucide-react'
import { listQuizzes, getUserAttempts, generateQuiz, QuizListItem, QuizAttemptItem } from '@/src/services/api'
import { getUserId } from '@/src/lib/auth'

const QuizzesTab: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'available' | 'completed'>('available')
  const [availableQuizzes, setAvailableQuizzes] = useState<QuizListItem[]>([])
  const [completedAttempts, setCompletedAttempts] = useState<QuizAttemptItem[]>([])
  const [loading, setLoading] = useState(true)
  const [generatingQuiz, setGeneratingQuiz] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const userId = getUserId()
        const [quizzes, attempts] = await Promise.all([
          listQuizzes(),
          userId ? getUserAttempts(userId) : Promise.resolve([]),
        ])
        setAvailableQuizzes(quizzes)
        setCompletedAttempts(attempts)
      } catch (err) {
        console.error('Failed to load quizzes:', err)
      } finally {
        setLoading(false)
      }

      // Auto-generate quiz if coming from syllabus
      const pendingTopic = sessionStorage.getItem('pending_quiz_topic')
      if (pendingTopic) {
        sessionStorage.removeItem('pending_quiz_topic')
        setGeneratingQuiz(pendingTopic)
        try {
          const quiz = await generateQuiz({
            topic: pendingTopic,
            topic_description: pendingTopic,
            user_id: getUserId(),
          })
          router.push(`/quiz?id=${quiz._id}`)
        } catch (err) {
          console.error('Failed to auto-generate quiz:', err)
          setGeneratingQuiz(null)
        }
      }
    }
    load()
  }, [])

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    return d.toLocaleDateString()
  }

  if (generatingQuiz) {
    return (
      <div className="p-6 flex flex-col items-center justify-center h-64 gap-4">
        <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
        <p className="text-lg font-medium text-gray-700">Generating quiz on &quot;{generatingQuiz}&quot;...</p>
        <p className="text-sm text-gray-500">This may take a few seconds</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Quizzes</h1>
        <p className="text-gray-600">Test your knowledge and track your learning progress</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab('available')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'available'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Available ({availableQuizzes.length})
        </button>
        <button
          onClick={() => setActiveTab('completed')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'completed'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Completed ({completedAttempts.length})
        </button>
      </div>

      {/* Available Quizzes */}
      {activeTab === 'available' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {availableQuizzes.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              <Brain className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="font-medium">No quizzes yet</p>
              <p className="text-sm mt-1">Generate a lesson first, then take a quiz!</p>
            </div>
          ) : (
            availableQuizzes.map((quiz) => (
              <div key={quiz._id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-teal-500 rounded-lg flex items-center justify-center">
                    <Brain className="w-6 h-6 text-white" />
                  </div>
                  <span className="px-2 py-1 rounded-full text-xs font-medium text-blue-600 bg-blue-100">
                    {quiz.question_count} Qs
                  </span>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">{quiz.topic}</h3>
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">{quiz.topic_description}</p>

                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <span className="flex items-center">
                    <Brain className="w-4 h-4 mr-1" />
                    {quiz.question_count} questions
                  </span>
                  <span className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {formatDate(quiz.created_at)}
                  </span>
                </div>

                <button
                  onClick={() => router.push(`/quiz?id=${quiz._id}`)}
                  className="w-full flex items-center justify-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <Play className="w-4 h-4" />
                  <span>Start Quiz</span>
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {/* Completed Quizzes */}
      {activeTab === 'completed' && (
        <div className="space-y-4">
          {completedAttempts.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <CheckCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="font-medium">No completed quizzes</p>
              <p className="text-sm mt-1">Take a quiz to see your results here</p>
            </div>
          ) : (
            completedAttempts.map((attempt) => (
              <div key={attempt._id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-gray-400 to-gray-500 rounded-lg flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-white" />
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Quiz {attempt.quiz_id.slice(-6)}</h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>{attempt.correct_count + attempt.wrong_count} questions</span>
                        <span>•</span>
                        <span className="flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {Math.round(attempt.time_taken_seconds / 60)} min
                        </span>
                        <span>•</span>
                        <span>{formatDate(attempt.completed_at)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getScoreColor(attempt.score)}`}>
                        {attempt.correct_count}/{attempt.correct_count + attempt.wrong_count}
                      </div>
                      <div className="text-sm text-gray-500">
                        {Math.round(attempt.score)}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default QuizzesTab