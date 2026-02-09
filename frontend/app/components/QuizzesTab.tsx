

'use client'
import QuizAttempt from './QuizAttempt'

import React, { useState } from 'react'
import { Brain, Clock, CheckCircle, XCircle, Play, Trophy, Star } from 'lucide-react'

interface QuizResult {
  id: string
  title: string
  subject: string
  score: number
  totalQuestions: number
  timeSpent: string
  date: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
}

const QuizzesTab: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'available' | 'completed'>('available')
  const [startQuiz, setStartQuiz] = useState(false)


  const availableQuizzes = [
    {
      id: '1',
      title: 'Photosynthesis Fundamentals',
      subject: 'Biology',
      questions: 10,
      difficulty: 'Easy' as const,
      estimatedTime: '8 min',
      description: 'Test your understanding of how plants convert sunlight into energy'
    },
    {
      id: '2',
      title: 'Newton\'s Laws of Motion',
      subject: 'Physics',
      questions: 15,
      difficulty: 'Medium' as const,
      estimatedTime: '12 min',
      description: 'Explore the fundamental principles of motion and force'
    },
    {
      id: '3',
      title: 'Chemical Bonding',
      subject: 'Chemistry',
      questions: 12,
      difficulty: 'Hard' as const,
      estimatedTime: '15 min',
      description: 'Master ionic, covalent, and metallic bonding concepts'
    },
    {
      id: '4',
      title: 'Cellular Respiration',
      subject: 'Biology',
      questions: 8,
      difficulty: 'Medium' as const,
      estimatedTime: '10 min',
      description: 'Learn how cells break down glucose to produce energy'
    }
  ]

  const completedQuizzes: QuizResult[] = [
    {
      id: '1',
      title: 'Basic Algebra',
      subject: 'Mathematics',
      score: 8,
      totalQuestions: 10,
      timeSpent: '7 min',
      date: '2 days ago',
      difficulty: 'Easy'
    },
    {
      id: '2',
      title: 'World War II',
      subject: 'History',
      score: 12,
      totalQuestions: 15,
      timeSpent: '11 min',
      date: '1 week ago',
      difficulty: 'Medium'
    },
    {
      id: '3',
      title: 'Ecosystem Dynamics',
      subject: 'Biology',
      score: 6,
      totalQuestions: 10,
      timeSpent: '9 min',
      date: '2 weeks ago',
      difficulty: 'Hard'
    }
  ]

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600 bg-green-100'
      case 'Medium': return 'text-yellow-600 bg-yellow-100'
      case 'Hard': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getScoreColor = (score: number, total: number) => {
    const percentage = (score / total) * 100
    if (percentage >= 80) return 'text-green-600'
    if (percentage >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }
  if (startQuiz) {
  return <QuizAttempt onEnd={() => setStartQuiz(false)} />
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
          Available Quizzes
        </button>
        <button
          onClick={() => setActiveTab('completed')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'completed'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Completed Quizzes
        </button>
      </div>

      {/* Available Quizzes */}
      {activeTab === 'available' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {availableQuizzes.map((quiz) => (
            <div key={quiz.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-teal-500 rounded-lg flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(quiz.difficulty)}`}>
                  {quiz.difficulty}
                </span>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{quiz.title}</h3>
              <p className="text-sm text-gray-600 mb-4">{quiz.description}</p>
              
              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span className="flex items-center">
                  <Brain className="w-4 h-4 mr-1" />
                  {quiz.questions} questions
                </span>
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {quiz.estimatedTime}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-600">{quiz.subject}</span>
                <button  
                  onClick={() => setStartQuiz(true)}
                  className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                  <Play className="w-4 h-4" />
                  <span>Start Quiz</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Completed Quizzes */}
      {activeTab === 'completed' && (
        <div className="space-y-4">
          {completedQuizzes.map((quiz) => (
            <div key={quiz.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-gray-400 to-gray-500 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-white" />
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{quiz.title}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{quiz.subject}</span>
                      <span>•</span>
                      <span className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {quiz.timeSpent}
                      </span>
                      <span>•</span>
                      <span>{quiz.date}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${getScoreColor(quiz.score, quiz.totalQuestions)}`}>
                      {quiz.score}/{quiz.totalQuestions}
                    </div>
                    <div className="text-sm text-gray-500">
                      {Math.round((quiz.score / quiz.totalQuestions) * 100)}%
                    </div>
                  </div>
                  
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(quiz.difficulty)}`}>
                    {quiz.difficulty}
                  </span>
                  
                  <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    Review
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default QuizzesTab