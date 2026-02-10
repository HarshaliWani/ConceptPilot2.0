'use client'
import { useRouter } from 'next/navigation'

import React, { useState, useEffect } from 'react'
import { ChevronDown, User, Settings, LogOut, BookOpen } from 'lucide-react'
import { getCurrentUser, clearAuth, isLoggedIn } from '@/src/lib/auth'

const Header: React.FC = () => {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [userName, setUserName] = useState('')
  const router = useRouter()

  useEffect(() => {
    const user = getCurrentUser()
    if (user) {
      setUserName(user.name || user.username || 'User')
    }
  }, [])

  const handleLogout = () => {
    clearAuth()
    setDropdownOpen(false)
    router.push('/login')
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4 fixed top-0 left-0 right-0 z-50">
      <div className="flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-teal-500 rounded-lg flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">ConceptPilot</h1>
            <p className="text-xs text-gray-500">AI Educational Tutor</p>
          </div>
        </div>

        {/* User Profile */}
        <div className="relative">
          {isLoggedIn() ? (
            <>
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center space-x-3 hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-teal-400 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">{userName}</p>
                  <p className="text-xs text-gray-500">Student</p>
                </div>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <button
                    onClick={() => { setDropdownOpen(false); router.push('/profile') }}
                    className="flex w-full items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Settings className="w-4 h-4 mr-3" />
                    Settings
                  </button>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <LogOut className="w-4 h-4 mr-3" />
                    Logout
                  </button>
                </div>
              )}
            </>
          ) : (
            <button
              onClick={() => router.push('/login')}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors"
            >
              Login
            </button>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header