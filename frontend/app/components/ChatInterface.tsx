'use client'

import React, { useState } from 'react'
import { Send, Bot, User, Mic } from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
}

interface ChatInterfaceProps {
  onQuizGenerated: (quiz: any) => void
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onQuizGenerated }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: "Hello! I'm ConceptPilot, your AI educational tutor. Ask me anything you'd like to learn about - I can explain concepts, provide examples, and create quizzes to help you master the material!",
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isListening, setIsListening] = useState(false)

  const sampleAIResponses = [
    {
      content: "Great question about photosynthesis! Let me break this down for you:\n\n**What is Photosynthesis?**\nPhotosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose (sugar) and oxygen. Think of it as nature's way of cooking food using sunlight as the energy source.\n\n**Real-life Example:**\nImagine your car's solar panels charging the battery - plants do something similar! The green leaves act like solar panels, capturing sunlight to power the 'cooking' process that creates food for the plant.\n\n**The Formula:**\n6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂\n\nThis process happens in the chloroplasts, tiny green factories inside plant cells!",
      quiz: {
        question: "What are the main inputs needed for photosynthesis?",
        options: [
          "Sunlight, water, and carbon dioxide",
          "Oxygen, glucose, and chlorophyll", 
          "Nitrogen, phosphorus, and potassium",
          "Heat, pressure, and minerals"
        ],
        correct: 0,
        explanation: "Photosynthesis requires sunlight (energy), water (H₂O), and carbon dioxide (CO₂) to produce glucose and oxygen."
      }
    },
    {
      content: "Let me explain gravity in a way that's easy to understand!\n\n**What is Gravity?**\nGravity is the force that attracts objects with mass toward each other. The more massive an object, the stronger its gravitational pull.\n\n**Sports Example:**\nWhen you shoot a basketball, gravity is what brings the ball back down to the court. If you're on the Moon (which has less mass than Earth), the same shot would go much higher and farther because the Moon's gravity is weaker!\n\n**Car Example:**\nWhen you drive down a steep hill, gravity helps accelerate your car downward. That's why you need to use your brakes to control your speed - you're fighting against gravity's pull.\n\n**Fun Fact:**\nEverything falls at the same rate in a vacuum - a feather and a hammer would hit the ground at the same time on the Moon!",
      quiz: {
        question: "Why do objects fall faster on Earth than on the Moon?",
        options: [
          "Earth has stronger gravity due to its larger mass",
          "The Moon has no atmosphere",
          "Earth spins faster than the Moon",
          "Objects don't actually fall faster on Earth"
        ],
        correct: 0,
        explanation: "Earth has much more mass than the Moon, creating a stronger gravitational field that pulls objects down with greater force."
      }
    }
  ]

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')

    // Simulate AI response
    setTimeout(() => {
      const randomResponse = sampleAIResponses[Math.floor(Math.random() * sampleAIResponses.length)]
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: randomResponse.content,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])
      
      // Generate quiz after AI response
      setTimeout(() => {
        onQuizGenerated(randomResponse.quiz)
      }, 1000)
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleVoiceInput = () => {
    setIsListening(!isListening)
    // Voice recognition logic would go here
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
              placeholder="Ask me anything you'd like to learn..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={1}
            />
          </div>
          <button
            onClick={handleVoiceInput}
            className={`px-4 py-3 rounded-lg transition-colors flex items-center justify-center ${
              isListening 
                ? 'bg-red-500 text-white hover:bg-red-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Mic className="w-5 h-5" />
          </button>
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim()}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        {isListening && (
          <div className="mt-2 flex items-center space-x-2 text-sm text-red-600">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span>Listening...</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatInterface