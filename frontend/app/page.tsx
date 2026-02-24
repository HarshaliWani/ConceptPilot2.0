'use client'

import React, { useState, useEffect, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { isLoggedIn } from '@/src/lib/auth'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import LearningDashboard from './components/LearningDashboard'
import QuizzesTab from './components/QuizzesTab'
import FlashcardsTab from './components/FlashcardsTab'
import ProgressTab from './components/ProgressTab'
import ProfileTab from './components/ProfileTab'


function HomeContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const tabParam = searchParams.get('tab')
  const [activeSection, setActiveSection] = useState('learning')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [showWelcome, setShowWelcome] = useState(false)
  const [authChecked, setAuthChecked] = useState(false)

  useEffect(() => {
    // Auth guard — redirect to login if not authenticated
    if (!isLoggedIn()) {
      router.replace('/login')
      return
    }
    setAuthChecked(true)
  }, [])

  useEffect(() => {
    // Handle ?tab=profile redirect from registration
    if (tabParam === 'profile') {
      setActiveSection('profile')
      setShowWelcome(true)
      // Clear welcome message after 5 seconds
      setTimeout(() => setShowWelcome(false), 5000)
    }
  }, [tabParam])

  if (!authChecked) return null

  return (
    <div className="min-h-screen bg-gray-50 pt-[80px]">
      <Header />
      
      {/* Welcome Banner */}
      {showWelcome && (
        <div className="fixed top-20 left-0 right-0 z-50 mx-4 mt-2">
          <div className="max-w-4xl mx-auto bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg shadow-lg flex items-center justify-between">
            <span className="font-medium">🎉 Welcome! Complete your profile to get personalized lessons.</span>
            <button 
              onClick={() => setShowWelcome(false)}
              className="text-green-700 hover:text-green-900 font-bold"
            >
              ✕
            </button>
          </div>
        </div>
      )}
      
      <div className="flex h-[calc(100vh-80px)]">
        <Sidebar 
          activeSection={activeSection} 
          onSectionChange={setActiveSection}
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
        
        <main className={`flex-1 overflow-y-auto transition-all duration-300 ${
  sidebarCollapsed ? 'ml-16' : 'ml-64'
        }`}>
          {activeSection === 'learning' && <LearningDashboard />}
          {activeSection === 'quizzes' && <QuizzesTab />}
          {activeSection === 'flashcards' && <FlashcardsTab />}
          {activeSection === 'progress' && <ProgressTab onSectionChange={setActiveSection} />}
          {activeSection === 'profile' && <ProfileTab />}

        </main>
      </div>
    </div>
  )
}
export default function Home() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading...</div>}>
      <HomeContent />
    </Suspense>
  )
}