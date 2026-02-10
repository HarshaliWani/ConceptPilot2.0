'use client'

import React, { useEffect } from 'react'
import { Play } from 'lucide-react'
import { useLessonStore } from '@/src/store/lessonStore'
import dynamic from 'next/dynamic'

// Dynamic import to avoid SSR issues with Konva
const LessonCanvas = dynamic(() => import('@/src/components/LessonCanvas'), { ssr: false })
const AudioController = dynamic(() => import('@/src/components/AudioController'), { ssr: false })

interface AITeachingBoardProps {
  lessonReady: boolean
}

const AITeachingBoard: React.FC<AITeachingBoardProps> = ({ lessonReady }) => {
  const { lessonData } = useLessonStore()

  if (!lessonReady || !lessonData) {
    return (
      <div className="h-full flex flex-col">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Teaching Board</h2>
          <span className="text-sm text-gray-600">
            Type a topic in the chat to generate a lesson
          </span>
        </div>

        <div className="flex-1 flex items-center justify-center">
          <div className="w-full h-full bg-white rounded-lg shadow-lg border-2 border-gray-200 flex items-center justify-center">
            <div className="text-center">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Play className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                Interactive Whiteboard
              </h3>
              <p className="text-gray-500 max-w-md">
                Type a topic in the chat to generate an AI lesson with 
                animated diagrams and narration.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">{lessonData.title}</h2>
        <span className="inline-block mt-1 px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
          {lessonData.topic}
        </span>
      </div>

      {/* Lesson Canvas */}
      <div className="flex-1 mb-4">
        <LessonCanvas />
      </div>

      {/* Audio Controller */}
      <div>
        <AudioController />
      </div>
    </div>
  )
}

export default AITeachingBoard