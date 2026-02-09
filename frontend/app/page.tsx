'use client'

import React, { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import LearningDashboard from './components/LearningDashboard'
import QuizzesTab from './components/QuizzesTab'
import FlashcardsTab from './components/FlashcardsTab'
import ProgressTab from './components/ProgressTab'
import ProfileTab from './components/ProfileTab'


export default function Home() {
  const [activeSection, setActiveSection] = useState('learning')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 pt-[80px]">
      <Header />
      
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
          {activeSection === 'progress' && <ProgressTab />}
          {activeSection === 'profile' && <ProfileTab />}

        </main>
      </div>
    </div>
  )
}