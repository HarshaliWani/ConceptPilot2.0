'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import ChatInterface from './ChatInterface'
import AITeachingBoard from './AITeachingBoard'
import { useLessonStore } from '@/src/store/lessonStore'
import { generateQuiz, LessonData } from '@/src/services/api'
import { getUserId } from '@/src/lib/auth'

const LearningDashboard: React.FC = () => {
  const [lessonReady, setLessonReady] = useState(false)
  const [generatingQuiz, setGeneratingQuiz] = useState(false)
  const { setLessonData, lessonData, resetPlayback } = useLessonStore()
  const router = useRouter()

  const handleLessonGenerated = (lesson: LessonData) => {
    resetPlayback()
    setLessonData(lesson)
    setLessonReady(true)
  }

  const handleTakeQuiz = async () => {
    if (!lessonData) return
    setGeneratingQuiz(true)
    try {
      const quiz = await generateQuiz({
        topic: lessonData.topic,
        topic_description: lessonData.title,
        lesson_id: lessonData._id,
        user_id: getUserId(),
      })
      router.push(`/quiz?id=${quiz._id}`)
    } catch (err) {
      console.error('Failed to generate quiz:', err)
      alert('Failed to generate quiz. Please try again.')
    } finally {
      setGeneratingQuiz(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-1 min-h-0">
        {/* AI Teaching Board */}
        <div className="w-1/2 p-6">
          <AITeachingBoard lessonReady={lessonReady} />
        </div>

        {/* Chat Interface */}
        <div className="w-1/2 flex flex-col bg-white border-l border-gray-200">
          <ChatInterface onLessonGenerated={handleLessonGenerated} />
        </div>
      </div>

      {/* Quiz prompt - shown after lesson is generated */}
      {lessonReady && lessonData && (
        <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-t border-blue-200">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-gray-900">Test Your Knowledge</h3>
              <p className="text-sm text-gray-600">Take a quiz on &quot;{lessonData.topic}&quot; to reinforce your learning</p>
            </div>
            <button
              onClick={handleTakeQuiz}
              disabled={generatingQuiz}
              className="px-5 py-2.5 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {generatingQuiz ? 'Generating...' : '📝 Take Quiz'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default LearningDashboard