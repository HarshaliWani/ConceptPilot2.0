'use client'

import React, { useMemo } from 'react'
import { MessageCircle } from 'lucide-react'

interface NarrationDisplayProps {
  narration: string
  title: string
  currentTime?: number
  duration?: number
}

const NarrationDisplay: React.FC<NarrationDisplayProps> = ({ 
  narration, 
  title, 
  currentTime = 0,
  duration = 0
}) => {
  // Split narration into words for real-time highlighting
  const words = useMemo(() => {
    return narration.split(/\s+/).filter(w => w.length > 0)
  }, [narration])

  // Estimate word timing based on average speech rate (~150 words per minute)
  const wordsWithTiming = useMemo(() => {
    const wordsPerSecond = 150 / 60 // ~2.5 words per second
    const wordDuration = 1 / wordsPerSecond // ~0.4 seconds per word

    return words.map((word, index) => ({
      word,
      startTime: index * wordDuration,
      endTime: (index + 1) * wordDuration
    }))
  }, [words])

  // Get current word being spoken
  const currentWordIndex = useMemo(() => {
    return wordsWithTiming.findIndex(
      w => currentTime >= w.startTime && currentTime < w.endTime
    )
  }, [currentTime, wordsWithTiming])

  // Format time display
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-white to-gray-50 rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <MessageCircle className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Narration</h3>
        </div>
        <p className="text-xs text-gray-600 truncate font-medium">{title}</p>
      </div>

      {/* Progress Bar */}
      {duration > 0 && (
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1.5">
            <span className="font-medium">{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      )}

      {/* Narration Text - with real-time word highlighting */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="text-sm leading-7 text-gray-800">
          {words.map((word, index) => {
            const isCurrentWord = index === currentWordIndex
            const isNextWord = index === currentWordIndex + 1
            
            return (
              <span
                key={index}
                className={`inline-block mr-1 transition-all duration-100 rounded px-1.5 py-0.5 ${
                  isCurrentWord
                    ? 'bg-yellow-300 font-bold text-gray-900 shadow-sm'
                    : isNextWord
                    ? 'bg-yellow-100 text-gray-800'
                    : 'text-gray-700'
                }`}
              >
                {word}
              </span>
            )
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-blue-50 border-t border-gray-200 text-xs text-blue-800">
        <p><strong>💡 Tip:</strong> The highlighted word is being spoken in real-time</p>
      </div>
    </div>
  )
}

export default NarrationDisplay
