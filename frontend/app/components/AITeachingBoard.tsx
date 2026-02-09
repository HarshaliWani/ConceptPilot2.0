'use client'

import React, { useState } from 'react'
import { Play, Pause } from 'lucide-react'

const AITeachingBoard: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false)

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
    // Future: This will control the whiteboard/canvas functionality
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Teaching Board</h2>
        <div className="flex items-center space-x-4">
          <button
            onClick={handlePlayPause}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              isPlaying 
                ? 'bg-red-500 text-white hover:bg-red-600' 
                : 'bg-green-500 text-white hover:bg-green-600'
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="w-5 h-5" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                <span>Play</span>
              </>
            )}
          </button>
          <span className="text-sm text-gray-600">
            {isPlaying ? 'AI is teaching...' : 'Ready to start lesson'}
          </span>
        </div>
      </div>

      {/* Canvas Placeholder */}
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
              This canvas will display AI-generated diagrams, illustrations, and interactive content 
              to enhance your learning experience.
            </p>
            <div className="mt-6 text-sm text-gray-400">
              Canvas component ready for integration
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AITeachingBoard