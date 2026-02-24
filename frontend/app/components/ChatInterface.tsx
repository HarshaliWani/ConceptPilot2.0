'use client'

import React, { useState, useEffect } from 'react'
import { Send, Bot, User, Mic, Loader2 } from 'lucide-react'
import { generateLesson, LessonData } from '@/src/services/api'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
}

interface ChatInterfaceProps {
  onLessonGenerated: (lesson: LessonData) => void
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onLessonGenerated }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  // Initialize the welcome message on mount (client only) to avoid hydration mismatch
  useEffect(() => {
    setMessages([
      {
        id: '1',
        type: 'ai',
        content: "Hello! I'm ConceptPilot, your AI educational tutor. Type a topic you'd like to learn about and I'll create an interactive lesson with animations and narration for you!",
        timestamp: new Date()
      }
    ])

    // Auto-trigger if a topic was pre-filled from the syllabus
    const prefilledTopic = sessionStorage.getItem('prefilled_topic')
    if (prefilledTopic) {
      sessionStorage.removeItem('prefilled_topic')
      setInputValue(prefilledTopic)
      // Slight delay to let messages state settle before triggering
      setTimeout(() => {
        triggerGeneration(prefilledTopic)
      }, 100)
    }
  }, [])

  const triggerGeneration = async (topic: string) => {
    if (!topic.trim()) return
    setIsGenerating(true)

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: topic,
      timestamp: new Date()
    }
    const loadingMsg: Message = {
      id: (Date.now() + 1).toString(),
      type: 'ai',
      content: `Generating a lesson on "${topic}"... This may take up to a minute while the AI creates your personalized content with animations and narration.`,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage, loadingMsg])
    setInputValue('')

    try {
      const lesson = await generateLesson({
        topic,
        user_interest: topic,
        proficiency_level: 'beginner',
      })
      const successMsg: Message = {
        id: (Date.now() + 2).toString(),
        type: 'ai',
        content: `Your lesson "${lesson.title}" is ready! Click the Play button on the teaching board to start learning!`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev.filter(m => m.id !== loadingMsg.id), successMsg])
      onLessonGenerated(lesson)
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      const errText = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((d: any) => d.msg).join(', ') : (err?.message || 'Please try again.')
      setMessages(prev => [...prev.filter(m => m.id !== loadingMsg.id), {
        id: (Date.now() + 3).toString(),
        type: 'ai',
        content: `Sorry, I couldn't generate that lesson. ${errText}`,
        timestamp: new Date()
      }])
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isGenerating) return
    await triggerGeneration(inputValue.trim())
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.type === 'ai' && (
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-teal-500 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            
            <div
              className={`max-w-md px-4 py-3 rounded-2xl ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white ml-auto'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </div>
              <div className={`text-xs mt-2 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>

            {message.type === 'user' && (
              <div className="w-8 h-8 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-6 border-t border-gray-200 bg-white">
        <div className="flex space-x-4">
          <div className="flex-1 relative">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isGenerating ? 'Generating lesson...' : "Type a topic to learn about (e.g., Photosynthesis, Gravity, DNA)..."}
              disabled={isGenerating}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:opacity-50"
              rows={1}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isGenerating}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {isGenerating ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface