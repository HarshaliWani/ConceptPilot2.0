'use client'

import React, { useState, useEffect } from 'react'
import { CreditCard, RotateCcw, ChevronLeft, ChevronRight, Plus, Trash2, Eye, EyeOff, Star, Loader2, Sparkles } from 'lucide-react'
import { 
  generateFlashcards, 
  getFlashcards, 
  getFlashcardTopics, 
  reviewFlashcard, 
  deleteFlashcard,
  Flashcard,
  FlashcardTopic 
} from '@/src/services/api'

const FlashcardsTab: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'generate' | 'study' | 'manage'>('generate')
  const [flashcards, setFlashcards] = useState<Flashcard[]>([])
  const [topics, setTopics] = useState<FlashcardTopic[]>([])
  const [selectedTopic, setSelectedTopic] = useState<string>('')
  const [customTopic, setCustomTopic] = useState('')
  const [isCustomMode, setIsCustomMode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  
  // Study mode state
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [isAnimating, setIsAnimating] = useState(false)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [studyFilter, setStudyFilter] = useState({ topic: '', difficulty: '' })
  
  // Syllabus topics
  const [syllabusTopics, setSyllabusTopics] = useState<string[]>([])

  useEffect(() => {
    loadTopics()
    loadSyllabusTopics()
  }, [])

  useEffect(() => {
    if (activeTab === 'study' || activeTab === 'manage') {
      loadFlashcards()
    }
  }, [activeTab, studyFilter])

  const loadSyllabusTopics = async () => {
    try {
      const response = await fetch('/syllabus.json')
      const data = await response.json()
      const allTopics: string[] = []
      data.forEach((subject: any) => {
        subject.modules.forEach((module: any) => {
          module.subTopics.forEach((topic: string) => {
            allTopics.push(topic)
          })
        })
      })
      setSyllabusTopics(allTopics)
    } catch (err) {
      console.error('Failed to load syllabus:', err)
    }
  }

  const loadTopics = async () => {
    try {
      const data = await getFlashcardTopics()
      setTopics(data)
    } catch (err) {
      console.error('Failed to load topics:', err)
    }
  }

  const loadFlashcards = async () => {
    setLoading(true)
    try {
      const filters: any = {}
      if (studyFilter.topic) filters.topic = studyFilter.topic
      if (studyFilter.difficulty) filters.difficulty = studyFilter.difficulty
      
      const data = await getFlashcards(filters)
      setFlashcards(data)
      setCurrentCardIndex(0)
      setIsFlipped(false)
    } catch (err) {
      console.error('Failed to load flashcards:', err)
      setMessage({ type: 'error', text: 'Failed to load flashcards' })
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    const topic = isCustomMode ? customTopic : selectedTopic
    
    if (!topic.trim()) {
      setMessage({ type: 'error', text: 'Please enter or select a topic' })
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      const generated = await generateFlashcards(topic, isCustomMode)
      setMessage({ type: 'success', text: `Generated ${generated.length} flashcards successfully!` })
      await loadTopics()
      
      // Switch to study tab and load the new flashcards
      setActiveTab('study')
      setStudyFilter({ topic, difficulty: '' })
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      setMessage({ type: 'error', text: detail || 'Failed to generate flashcards' })
    } finally {
      setLoading(false)
    }
  }

  const handleReview = async (confidence: number) => {
    if (!flashcards[currentCardIndex]) return

    try {
      await reviewFlashcard(flashcards[currentCardIndex]._id, confidence)
      setMessage({ type: 'success', text: 'Progress saved!' })
      setTimeout(() => setMessage(null), 2000)
      
      // Move to next card
      handleNextCard()
    } catch (err) {
      console.error('Failed to review flashcard:', err)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteFlashcard(id)
      setMessage({ type: 'success', text: 'Flashcard deleted' })
      await loadFlashcards()
      await loadTopics()
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to delete flashcard' })
    }
  }

  const handleNextCard = () => {
    if (isTransitioning) return
    
    setIsTransitioning(true)
    setIsFlipped(false)
    
    setTimeout(() => {
      setCurrentCardIndex((prev) => (prev + 1) % flashcards.length)
      setIsTransitioning(false)
    }, 350) // Half of the flip animation duration
  }

  const handlePrevCard = () => {
    if (isTransitioning) return
    
    setIsTransitioning(true)
    setIsFlipped(false)
    
    setTimeout(() => {
      setCurrentCardIndex((prev) => (prev - 1 + flashcards.length) % flashcards.length)
      setIsTransitioning(false)
    }, 350)
  }

  const handleFlip = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (isAnimating || isTransitioning) return
    
    setIsAnimating(true)
    setIsFlipped(!isFlipped)
    
    // Reset animation state after transition completes
    setTimeout(() => setIsAnimating(false), 700)
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'hard': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const currentCard = flashcards[currentCardIndex]

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Flashcards</h1>
        <p className="text-gray-600">Generate, study, and manage your flashcards</p>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${
          message.type === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-700' 
            : 'bg-red-50 border border-red-200 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab('generate')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'generate'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Sparkles className="w-4 h-4 inline-block mr-1" />
          Generate
        </button>
        <button
          onClick={() => setActiveTab('study')}
          disabled={flashcards.length === 0 && activeTab !== 'generate'}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'study'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          } disabled:opacity-50`}
        >
          Study Mode
        </button>
        <button
          onClick={() => setActiveTab('manage')}
          disabled={flashcards.length === 0 && activeTab !== 'generate'}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'manage'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          } disabled:opacity-50`}
        >
          Manage Cards
        </button>
      </div>

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Generate Flashcards with AI</h2>
            
            <div className="mb-6">
              <div className="flex space-x-4 mb-4">
                <button
                  onClick={() => setIsCustomMode(false)}
                  className={`flex-1 py-2 px-4 rounded-lg border-2 transition-all ${
                    !isCustomMode 
                      ? 'border-blue-500 bg-blue-50 text-blue-700' 
                      : 'border-gray-200 text-gray-600 hover:border-gray-300'
                  }`}
                >
                  From Syllabus
                </button>
                <button
                  onClick={() => setIsCustomMode(true)}
                  className={`flex-1 py-2 px-4 rounded-lg border-2 transition-all ${
                    isCustomMode 
                      ? 'border-blue-500 bg-blue-50 text-blue-700' 
                      : 'border-gray-200 text-gray-600 hover:border-gray-300'
                  }`}
                >
                  Custom Topic
                </button>
              </div>

              {!isCustomMode ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Syllabus Topic
                  </label>
                  <select
                    value={selectedTopic}
                    onChange={(e) => setSelectedTopic(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Choose a topic...</option>
                    {syllabusTopics.map((topic, idx) => (
                      <option key={idx} value={topic}>
                        {topic.substring(0, 100)}{topic.length > 100 ? '...' : ''}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Enter Custom Topic
                  </label>
                  <input
                    type="text"
                    value={customTopic}
                    onChange={(e) => setCustomTopic(e.target.value)}
                    placeholder="e.g., Quantum Mechanics, World War II, Python Data Structures..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> 10 flashcards will be generated with varied difficulty levels (easy, medium, hard) to help you master the topic.
              </p>
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>Generate Flashcards</span>
                </>
              )}
            </button>

            {topics.length > 0 && (
              <div className="mt-8 pt-6 border-t">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Your Topics ({topics.length})</h3>
                <div className="flex flex-wrap gap-2">
                  {topics.map((topic, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {topic.topic.substring(0, 40)}{topic.topic.length > 40 ? '...' : ''} ({topic.count})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Study Mode */}
      {activeTab === 'study' && (
        <div className="max-w-4xl mx-auto">
          {/* Filters */}
          <div className="mb-6 flex space-x-4">
            <select
              value={studyFilter.topic}
              onChange={(e) => setStudyFilter({ ...studyFilter, topic: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Topics</option>
              {topics.map((topic, idx) => (
                <option key={idx} value={topic.topic}>{topic.topic.substring(0, 50)}</option>
              ))}
            </select>
            <select
              value={studyFilter.difficulty}
              onChange={(e) => setStudyFilter({ ...studyFilter, difficulty: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
          ) : flashcards.length === 0 ? (
            <div className="text-center py-12">
              <CreditCard className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No flashcards yet. Generate some to get started!</p>
            </div>
          ) : currentCard && (
            <div className="mb-8">
              <div className="text-center mb-4">
                <span className="text-sm text-gray-500">
                  Card {currentCardIndex + 1} of {flashcards.length}
                </span>
              </div>

              <div 
                className={`relative w-full h-80 mx-auto cursor-pointer select-none transition-opacity duration-300 ${
                  isTransitioning ? 'opacity-0' : 'opacity-100'
                }`}
                style={{ perspective: '1000px' }}
                onClick={handleFlip}
              >
                <div
                  className="absolute inset-0 w-full h-full transition-transform duration-700 ease-in-out"
                  style={{
                    transformStyle: 'preserve-3d',
                    transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
                  }}
                >
                  {/* Front of card */}
                  <div
                    className="absolute inset-0 w-full h-full bg-white rounded-xl shadow-lg border border-gray-200 p-8 flex flex-col justify-center items-center select-none"
                    style={{ backfaceVisibility: 'hidden' }}
                  >
                    <div className="flex items-center justify-center w-full mb-6">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(currentCard.difficulty)}`}>
                        {currentCard.difficulty}
                      </span>
                    </div>
                    
                    <div className="text-center flex-1 flex items-center justify-center px-4">
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
                  <div
                    className="absolute inset-0 w-full h-full bg-blue-50 rounded-xl shadow-lg border border-blue-200 p-8 flex flex-col justify-center items-center select-none"
                    style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
                  >
                    <div className="flex items-center justify-center w-full mb-6">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(currentCard.difficulty)}`}>
                        {currentCard.difficulty}
                      </span>
                    </div>
                    
                    <div className="text-center flex-1 flex items-center justify-center px-4">
                      <div>
                        <p className="text-lg text-gray-800 leading-relaxed mb-4">
                          {currentCard.back}
                        </p>
                        {currentCard.explanation && (
                          <p className="text-sm text-gray-600 italic">
                            {currentCard.explanation}
                          </p>
                        )}
                      </div>
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
                  disabled={flashcards.length <= 1 || isTransitioning}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                  <span>Previous</span>
                </button>

                <button
                  onClick={handleFlip}
                  disabled={isAnimating || isTransitioning}
                  className="flex items-center space-x-2 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <RotateCcw className="w-5 h-5" />
                  <span>Flip Card</span>
                </button>

                <button
                  onClick={handleNextCard}
                  disabled={flashcards.length <= 1 || isTransitioning}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <span>Next</span>
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>

              {/* Confidence Rating */}
              {isFlipped && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-3 text-center">Rate your confidence (1-5 stars)</p>
                  <div className="flex justify-center space-x-2">
                    {[1, 2, 3, 4, 5].map((rating) => (
                      <button
                        key={rating}
                        onClick={() => handleReview(rating)}
                        className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                        title={`${rating} star${rating > 1 ? 's' : ''}`}
                      >
                        <Star className={`w-8 h-8 ${
                          rating === 1 ? 'text-red-500' : 
                          rating === 2 ? 'text-orange-500' : 
                          rating === 3 ? 'text-yellow-500' : 
                          rating === 4 ? 'text-lime-500' : 
                          'text-green-500'
                        }`} fill="currentColor" />
                      </button>
                    ))}
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
            <select
              value={studyFilter.topic}
              onChange={(e) => setStudyFilter({ ...studyFilter, topic: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Topics</option>
              {topics.map((topic, idx) => (
                <option key={idx} value={topic.topic}>{topic.topic.substring(0, 50)}</option>
              ))}
            </select>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
          ) : flashcards.length === 0 ? (
            <div className="text-center py-12">
              <CreditCard className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No flashcards to manage.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {flashcards.map((card) => (
                <div key={card._id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(card.difficulty)}`}>
                      {card.difficulty}
                    </span>
                    <button 
                      onClick={() => handleDelete(card._id)}
                      className="text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2">
                    {card.front}
                  </h3>
                  <p className="text-xs text-gray-600 mb-4 line-clamp-3">
                    {card.back}
                  </p>
                  
                  <div className="text-xs text-gray-500">
                    <div className="mb-2">Topic: {card.topic.substring(0, 40)}...</div>
                    <div>Confidence: {card.confidence}/5 stars</div>
                    <div>Reviews: {card.repetitions}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default FlashcardsTab
