'use client'

import React, { useState, useEffect } from 'react'
import { getCurrentUser, AuthUser, updateUser as updateLocalUser } from '@/src/lib/auth'
import { updateProfile } from '@/src/services/api'

const COURSE_CODES = [
  { code: 'BSC101', name: 'Applied Mathematics-I' },
  { code: 'BSC102', name: 'Applied Physics' },
  { code: 'BSC103', name: 'Applied Chemistry' },
  { code: 'ESC101', name: 'Engineering Mechanics' },
  { code: 'ESC102', name: 'Basic Electrical Engineering' },
  { code: 'AEC101', name: 'Communication Skills' },
  { code: 'VSEC102', name: 'C Programming' },
  { code: 'CC101', name: 'Human Values & Professional Ethics' },
]

export default function ProfileTab() {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [hobby, setHobby] = useState('')
  const [courseCode, setCourseCode] = useState('')
  const [year, setYear] = useState<number>(1)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  useEffect(() => {
    const u = getCurrentUser()
    if (u) {
      setUser(u)
      setHobby(u.hobby || '')
      setCourseCode(u.course_code || '')
      setYear(u.year || 1)
    }
  }, [])

  const handleSave = async () => {
    setLoading(true)
    setMessage(null)
    
    try {
      const updates = {
        hobby: hobby.trim() || undefined,
        course_code: courseCode || undefined,
        year: year || undefined,
      }
      
      const updatedUser = await updateProfile(updates)
      updateLocalUser(updatedUser)
      setUser(updatedUser)
      setMessage({ type: 'success', text: 'Profile updated successfully!' })
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      const msg = typeof detail === 'string' ? detail : 'Failed to update profile'
      setMessage({ type: 'error', text: msg })
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="p-6 max-w-4xl">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Profile</h1>
        <p className="text-gray-500">Please log in to view your profile.</p>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">
        Profile
      </h1>

      {message && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${
          message.type === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-700' 
            : 'bg-red-50 border border-red-200 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      <div className="bg-white rounded-xl shadow p-6 space-y-6">
        
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Name
          </label>
          <input
            type="text"
            defaultValue={user.name || ''}
            readOnly
            className="w-full rounded-lg border border-gray-300 px-4 py-2 bg-gray-50 text-gray-700"
          />
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            defaultValue={user.email || ''}
            readOnly
            className="w-full rounded-lg border border-gray-300 px-4 py-2 bg-gray-50 text-gray-700"
          />
        </div>

        {/* Username */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <input
            type="text"
            defaultValue={user.username || ''}
            readOnly
            className="w-full rounded-lg border border-gray-300 px-4 py-2 bg-gray-50 text-gray-700"
          />
        </div>

        {/* Grade Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Grade Level
          </label>
          <input
            type="text"
            defaultValue={user.grade_level || 'Not set'}
            readOnly
            className="w-full rounded-lg border border-gray-300 px-4 py-2 bg-gray-50 text-gray-700"
          />
        </div>

        <div className="border-t pt-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Complete Your Profile</h2>

          {/* Hobby */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hobby / Interest
            </label>
            <input
              type="text"
              value={hobby}
              onChange={(e) => setHobby(e.target.value)}
              placeholder="e.g., Basketball, Guitar, Reading..."
              className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">This helps personalize your lessons!</p>
          </div>

          {/* Course Code */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Course
            </label>
            <select
              value={courseCode}
              onChange={(e) => setCourseCode(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a course...</option>
              {COURSE_CODES.map(course => (
                <option key={course.code} value={course.code}>
                  {course.code} - {course.name}
                </option>
              ))}
            </select>
          </div>

          {/* Year */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Year of Study
            </label>
            <select
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>1st Year</option>
              <option value={2}>2nd Year</option>
              <option value={3}>3rd Year</option>
              <option value={4}>4th Year</option>
            </select>
          </div>

          <button
            onClick={handleSave}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Save Profile'}
          </button>
        </div>

        {/* Topic Proficiency */}
        {user.topic_proficiency && Object.keys(user.topic_proficiency).length > 0 && (
          <div className="border-t pt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Topic Proficiency
            </label>
            <div className="space-y-3">
              {Object.entries(user.topic_proficiency).map(([topic, score]) => (
                <div key={topic}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-700 capitalize">{topic}</span>
                    <span className="text-sm font-medium text-gray-900">{Math.round(score)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-blue-500"
                      style={{ width: `${Math.min(100, score)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
