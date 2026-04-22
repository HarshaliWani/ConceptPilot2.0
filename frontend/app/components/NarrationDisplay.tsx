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
  // Split narration into sentences for highlighting
  const sentences = useMemo(() => {
    // Split by common sentence endings while preserving punctuation
    const parts = narration.split(/(?<=[.!?])\s+/)
    return parts.map(s => s.trim()).filter(s => s.length > 0)
  }, [narration])

  // Estimate word timing based on average speech rate (~150 words per minute)
  // Create word-level timing for highlighting
  const wordsWithTiming = useMemo(() => {
    const words: Array<{ word: string; startTime: number; endTime: number }> = []
    const wordsPerSecond = 150 / 60 // ~2.5 words per second

    let currentSeconds = 0
    const allWords = narration.split(/\s+/)

    allWords.forEach((word) => {
      const wordDuration = 1 / wordsPerSecond // ~0.4 seconds per word
      words.push({
        word,
        startTime: currentSeconds,
        endTime: currentSeconds + wordDuration
      })
      currentSeconds += wordDuration
    })

    return words
  }, [narration])

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
    <div className="h-full flex flex-col bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <MessageCircle className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">Narration</h3>
        </div>
        <p className="text-sm text-gray-600 truncate">{title}</p>
      </div>

      {/* Progress Bar */}
      {duration > 0 && (
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
          <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      )}

      {/* Narration Text */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        <div className="text-sm leading-relaxed text-gray-800">
          {narration.split(/\s+/).map((word, index) => {
            const isCurrentWord = index === currentWordIndex
            return (
              <span
                key={index}
                className={`transition-all duration-200 ${
                  isCurrentWord
                    ? 'bg-yellow-200 font-semibold px-1 py-0.5 rounded'
                    : 'hover:bg-gray-100'
                }`}
              >
                {word}{' '}
              </span>
            )
          })}
        </div>
      </div>

      {/* Footer with tips */}
      <div className="px-4 py-3 bg-blue-50 border-t border-gray-200 text-xs text-gray-600">
        <p>💡 <strong>Tip:</strong> The highlighted word shows what's being spoken right now</p>
      </div>
    </div>
  )
}

export default NarrationDisplay
