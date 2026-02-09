'use client'

import React from 'react'
import { TrendingUp, Target, Award, Calendar, BookOpen, Brain, Clock, Star } from 'lucide-react'

const ProgressTab: React.FC = () => {
  const stats = [
    {
      label: 'Quizzes Completed',
      value: '24',
      change: '+3 this week',
      icon: Brain,
      color: 'blue'
    },
    {
      label: 'Average Score',
      value: '85%',
      change: '+5% from last month',
      icon: Target,
      color: 'green'
    },
    {
      label: 'Study Streak',
      value: '12 days',
      change: 'Keep it up!',
      icon: Calendar,
      color: 'orange'
    },
    {
      label: 'Time Studied',
      value: '47h',
      change: '+8h this month',
      icon: Clock,
      color: 'purple'
    }
  ]

  const subjects = [
    { name: 'Biology', progress: 85, quizzes: 8, color: 'green' },
    { name: 'Physics', progress: 72, quizzes: 6, color: 'blue' },
    { name: 'Chemistry', progress: 68, quizzes: 5, color: 'red' },
    { name: 'Mathematics', progress: 91, quizzes: 10, color: 'purple' },
    { name: 'History', progress: 76, quizzes: 4, color: 'yellow' }
  ]

  const recentActivity = [
    {
      type: 'quiz',
      title: 'Photosynthesis Fundamentals',
      subject: 'Biology',
      score: '9/10',
      time: '2 hours ago',
      icon: Brain
    },
    {
      type: 'study',
      title: 'Newton\'s Laws Study Session',
      subject: 'Physics',
      duration: '45 min',
      time: '1 day ago',
      icon: BookOpen
    },
    {
      type: 'achievement',
      title: 'Biology Master Badge',
      description: 'Completed 10 biology quizzes',
      time: '2 days ago',
      icon: Award
    },
    {
      type: 'quiz',
      title: 'Chemical Bonding',
      subject: 'Chemistry',
      score: '7/12',
      time: '3 days ago',
      icon: Brain
    }
  ]

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      red: 'bg-red-500',
      purple: 'bg-purple-500',
      yellow: 'bg-yellow-500',
      orange: 'bg-orange-500'
    }
    return colors[color as keyof typeof colors] || 'bg-gray-500'
  }

  const getIconBgColor = (color: string) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      red: 'bg-red-100 text-red-600',
      purple: 'bg-purple-100 text-purple-600',
      yellow: 'bg-yellow-100 text-yellow-600',
      orange: 'bg-orange-100 text-orange-600'
    }
    return colors[color as keyof typeof colors] || 'bg-gray-100 text-gray-600'
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
                <TrendingUp className="w-5 h-5 text-green-500" />
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-sm text-gray-600 mb-2">{stat.label}</div>
              <div className="text-xs text-green-600 font-medium">{stat.change}</div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Subject Progress */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Subject Progress</h2>
          <div className="space-y-6">
            {subjects.map((subject, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">{subject.name}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">{subject.quizzes} quizzes</span>
                    <span className="text-sm font-medium text-gray-900">{subject.progress}%</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getColorClasses(subject.color)}`}
                    style={{ width: `${subject.progress}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => {
              const Icon = activity.icon
              return (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-gray-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {activity.title}
                      </p>
                      <span className="text-xs text-gray-500">{activity.time}</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      {activity.subject && (
                        <span className="text-xs text-blue-600 font-medium">{activity.subject}</span>
                      )}
                      {activity.score && (
                        <span className="text-xs text-green-600 font-medium">{activity.score}</span>
                      )}
                      {activity.duration && (
                        <span className="text-xs text-purple-600 font-medium">{activity.duration}</span>
                      )}
                      {activity.description && (
                        <span className="text-xs text-gray-600">{activity.description}</span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Achievements Section */}
      <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Recent Achievements</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center">
              <Star className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Quiz Master</p>
              <p className="text-xs text-gray-600">Completed 25 quizzes</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
              <Award className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Biology Expert</p>
              <p className="text-xs text-gray-600">90% average in Biology</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Consistent Learner</p>
              <p className="text-xs text-gray-600">12-day study streak</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProgressTab