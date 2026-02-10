'use client'

import React, { useState, useEffect } from 'react'
import { TrendingUp, Target, Brain, Clock, Loader2 } from 'lucide-react'
import { getUserAttempts, QuizAttemptItem } from '@/src/services/api'
import { getUserId, getCurrentUser } from '@/src/lib/auth'

const ProgressTab: React.FC = () => {
  const [attempts, setAttempts] = useState<QuizAttemptItem[]>([])
  const [loading, setLoading] = useState(true)
  const [proficiency, setProficiency] = useState<Record<string, number>>({})

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const userId = getUserId()
        const data = await getUserAttempts(userId)
        setAttempts(data)

        // Get topic proficiency from user profile
        const user = getCurrentUser()
        if (user?.topic_proficiency) {
          setProficiency(user.topic_proficiency)
        }
      } catch (err) {
        console.error('Failed to load progress:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Compute stats from real data
  const totalQuizzes = attempts.length
  const avgScore = totalQuizzes > 0
    ? Math.round(attempts.reduce((sum, a) => sum + a.score, 0) / totalQuizzes)
    : 0
  const totalTime = attempts.reduce((sum, a) => sum + a.time_taken_seconds, 0)
  const totalTimeStr = totalTime >= 3600
    ? `${Math.round(totalTime / 3600)}h`
    : `${Math.round(totalTime / 60)}m`
  const totalCorrect = attempts.reduce((sum, a) => sum + a.correct_count, 0)
  const totalQuestions = attempts.reduce((sum, a) => sum + a.correct_count + a.wrong_count, 0)
  const overallAccuracy = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0

  const stats = [
    { label: 'Quizzes Completed', value: String(totalQuizzes), icon: Brain, color: 'blue' },
    { label: 'Average Score', value: `${avgScore}%`, icon: Target, color: 'green' },
    { label: 'Overall Accuracy', value: `${overallAccuracy}%`, icon: TrendingUp, color: 'purple' },
    { label: 'Total Time', value: totalTimeStr, icon: Clock, color: 'orange' },
  ]

  const getIconBgColor = (color: string) => {
    const colors: Record<string, string> = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      purple: 'bg-purple-100 text-purple-600',
      orange: 'bg-orange-100 text-orange-600',
    }
    return colors[color] || 'bg-gray-100 text-gray-600'
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
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Progress Dashboard</h1>
        <p className="text-gray-600">Track your learning journey and achievements</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getIconBgColor(stat.color)}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Topic Proficiency */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Topic Proficiency</h2>
          {Object.keys(proficiency).length === 0 ? (
            <p className="text-gray-500 text-sm">Take some quizzes to build your proficiency profile.</p>
          ) : (
            <div className="space-y-6">
              {Object.entries(proficiency)
                .sort(([, a], [, b]) => b - a)
                .map(([topic, score]) => (
                  <div key={topic}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900 capitalize">{topic}</span>
                      <span className="text-sm font-medium text-gray-900">{Math.round(score)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.min(100, score)}%` }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Recent Quiz Attempts */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Recent Activity</h2>
          {attempts.length === 0 ? (
            <p className="text-gray-500 text-sm">No quiz attempts yet. Start learning!</p>
          ) : (
            <div className="space-y-4">
              {attempts.slice(0, 8).map((attempt) => (
                <div key={attempt._id} className="flex items-start space-x-3">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Brain className="w-5 h-5 text-gray-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        Quiz Attempt
                      </p>
                      <span className="text-xs text-gray-500">{formatDate(attempt.completed_at)}</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`text-xs font-medium ${attempt.score >= 80 ? 'text-green-600' : attempt.score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {attempt.correct_count}/{attempt.correct_count + attempt.wrong_count} ({Math.round(attempt.score)}%)
                      </span>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-500">
                        {Math.round(attempt.time_taken_seconds / 60)} min
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProgressTab