'use client'

import React, { useState } from 'react'
import ChatInterface from './ChatInterface'
import QuizSection from './QuizSection'
import AITeachingBoard from './AITeachingBoard'

const LearningDashboard: React.FC = () => {
  const [currentQuiz, setCurrentQuiz] = useState(null)

  const handleQuizGenerated = (quiz: any) => {
    setCurrentQuiz(quiz)
  }

  return (
    <div className="flex h-full">
      {/* AI Teaching Board */}
      <div className="w-1/2 p-6">
        <AITeachingBoard />
      </div>

      {/* Chat and Quiz Section */}
      <div className="w-1/2 flex flex-col">
        {/* Chat Interface */}
        <div className="flex-1 bg-white border-l border-gray-200">
          <ChatInterface onQuizGenerated={handleQuizGenerated} />
        </div>
        
        {/* Quiz Section */}
        <div className="h-96 p-6 bg-gray-50 border-l border-t border-gray-200">
          <QuizSection quiz={currentQuiz} />
        </div>
      </div>
    </div>
  )
}

export default LearningDashboard