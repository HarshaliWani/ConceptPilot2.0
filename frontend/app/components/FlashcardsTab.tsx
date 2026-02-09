'use client'

import React, { useState } from 'react'
import { CreditCard, RotateCcw, ChevronLeft, ChevronRight, Plus, CreditCard as Edit, Trash2, Eye, EyeOff } from 'lucide-react'

interface Flashcard {
  id: string
  front: string
  back: string
  subject: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
  lastReviewed: string
  confidence: number
}

const FlashcardsTab: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'study' | 'manage'>('study')
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState('All')

  const flashcards: Flashcard[] = [
    {
      id: '1',
      front: 'What is photosynthesis?',
      back: 'Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen using chlorophyll.',
      subject: 'Biology',
      difficulty: 'Easy',
      lastReviewed: '2 days ago',
      confidence: 85
    },
    {
      id: '2',
      front: 'What is Newton\'s First Law of Motion?',
      back: 'An object at rest stays at rest and an object in motion stays in motion with the same speed and in the same direction unless acted upon by an unbalanced force.',
      subject: 'Physics',
      difficulty: 'Medium',
      lastReviewed: '1 day ago',
      confidence: 72
    },
    {
      id: '3',
      front: 'What is the chemical formula for water?',
      back: 'H₂O - Two hydrogen atoms bonded to one oxygen atom.',
      subject: 'Chemistry',
      difficulty: 'Easy',
      lastReviewed: '3 days ago',
      confidence: 95
    },
    {
      id: '4',
      front: 'What is the Pythagorean theorem?',
      back: 'In a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides: a² + b² = c²',
      subject: 'Mathematics',
      difficulty: 'Medium',
      lastReviewed: '1 week ago',
      confidence: 68
    },
    {
      id: '5',
      front: 'What causes the seasons on Earth?',
      back: 'Earth\'s seasons are caused by the tilt of Earth\'s axis (23.5°) as it orbits the sun, not by distance from the sun.',
      subject: 'Earth Science',
      difficulty: 'Hard',
      lastReviewed: '5 days ago',
      confidence: 45
    }
  ]

  const subjects = ['All', 'Biology', 'Physics', 'Chemistry', 'Mathematics', 'Earth Science']

  const filteredCards = selectedSubject === 'All' 
    ? flashcards 
    : flashcards.filter(card => card.subject === selectedSubject)

  const currentCard = filteredCards[currentCardIndex]

  const handleNextCard = () => {
    setCurrentCardIndex((prev) => (prev + 1) % filteredCards.length)
    setIsFlipped(false)
  }

  const handlePrevCard = () => {
    setCurrentCardIndex((prev) => (prev - 1 + filteredCards.length) % filteredCards.length)
    setIsFlipped(false)
  }

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600 bg-green-100'
      case 'Medium': return 'text-yellow-600 bg-yellow-100'
      case 'Hard': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600'
    if (confidence >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Flashcards</h1>
        <p className="text-gray-600">Review and manage your study flashcards</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab('study')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'study'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Study Mode
        </button>
        <button
          onClick={() => setActiveTab('manage')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'manage'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Manage Cards
        </button>
      </div>

      {/* Study Mode */}
      {activeTab === 'study' && (
        <div className="max-w-4xl mx-auto">
          {/* Subject Filter */}
          <div className="mb-6">
            <div className="flex flex-wrap gap-2">
              {subjects.map((subject) => (
                <button
                  key={subject}
                  onClick={() => {
                    setSelectedSubject(subject)
                    setCurrentCardIndex(0)
                    setIsFlipped(false)
                  }}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    selectedSubject === subject
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {subject}
                </button>
              ))}
            </div>
          </div>

          {/* Flashcard */}
          {currentCard && (
            <div className="mb-8">
              <div className="text-center mb-4">
                <span className="text-sm text-gray-500">
                  Card {currentCardIndex + 1} of {filteredCards.length}
                </span>
              </div>

              <div 
                className="relative w-full h-80 mx-auto cursor-pointer"
                onClick={handleFlip}
              >
                <div className={`absolute inset-0 w-full h-full transition-transform duration-500 transform-style-preserve-3d ${
                  isFlipped ? 'rotate-y-180' : ''
                }`}>
                  {/* Front of card */}
                  <div className="absolute inset-0 w-full h-full backface-hidden bg-white rounded-xl shadow-lg border border-gray-200 p-8 flex flex-col justify-center items-center">
                    <div className="flex items-center justify-between w-full mb-6">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(currentCard.difficulty)}`}>
                        {currentCard.difficulty}
                      </span>
                      <span className="text-sm font-medium text-blue-600">{currentCard.subject}</span>
                    </div>
                    
                    <div className="text-center flex-1 flex items-center justify-center">
                      <h3 className="text-xl font-semibold text-gray-900 leading-relaxed">
                        {currentCard.front}
                      </h3>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-500 mt-6">
                      <Eye className="w-4 h-4 mr-2" />
                      Click to reveal answer
                    </div>
                  </div>

                  {/* Back of card */}
                  <div className="absolute inset-0 w-full h-full backface-hidden rotate-y-180 bg-blue-50 rounded-xl shadow-lg border border-blue-200 p-8 flex flex-col justify-center items-center">
                    <div className="flex items-center justify-between w-full mb-6">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(currentCard.difficulty)}`}>
                        {currentCard.difficulty}
                      </span>
                      <span className="text-sm font-medium text-blue-600">{currentCard.subject}</span>
                    </div>
                    
                    <div className="text-center flex-1 flex items-center justify-center">
                      <p className="text-lg text-gray-800 leading-relaxed">
                        {currentCard.back}
                      </p>
                    </div>
                    
                    <div className="flex items-center text-sm text-blue-600 mt-6">
                      <EyeOff className="w-4 h-4 mr-2" />
                      Click to show question
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation Controls */}
              <div className="flex items-center justify-between mt-8">
                <button
                  onClick={handlePrevCard}
                  disabled={filteredCards.length <= 1}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                  <span>Previous</span>
                </button>

                <button
                  onClick={handleFlip}
                  className="flex items-center space-x-2 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <RotateCcw className="w-5 h-5" />
                  <span>Flip Card</span>
                </button>

                <button
                  onClick={handleNextCard}
                  disabled={filteredCards.length <= 1}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <span>Next</span>
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>

              {/* Confidence Rating */}
              {isFlipped && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-3">How confident are you with this card?</p>
                  <div className="flex space-x-2">
                    <button className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm">
                      Need Practice
                    </button>
                    <button className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors text-sm">
                      Getting There
                    </button>
                    <button className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors text-sm">
                      Got It!
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Manage Cards */}
      {activeTab === 'manage' && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {subjects.map((subject) => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>
            
            <button className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
              <Plus className="w-5 h-5" />
              <span>Add Card</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCards.map((card) => (
              <div key={card.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(card.difficulty)}`}>
                    {card.difficulty}
                  </span>
                  <div className="flex space-x-2">
                    <button className="text-gray-400 hover:text-blue-600 transition-colors">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="text-gray-400 hover:text-red-600 transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2">
                  {card.front}
                </h3>
                <p className="text-xs text-gray-600 mb-4 line-clamp-3">
                  {card.back}
                </p>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="font-medium text-blue-600">{card.subject}</span>
                  <span>Last reviewed: {card.lastReviewed}</span>
                </div>
                
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-gray-500">Confidence</span>
                  <span className={`text-xs font-medium ${getConfidenceColor(card.confidence)}`}>
                    {card.confidence}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                  <div
                    className={`h-1.5 rounded-full ${
                      card.confidence >= 80 ? 'bg-green-500' : 
                      card.confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${card.confidence}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default FlashcardsTab