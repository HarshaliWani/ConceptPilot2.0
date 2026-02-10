'use client'

import React, { useState, useEffect } from 'react'
import { getCurrentUser, AuthUser } from '@/src/lib/auth'

export default function ProfileTab() {
  const [user, setUser] = useState<AuthUser | null>(null)

  useEffect(() => {
    const u = getCurrentUser()
    if (u) setUser(u)
  }, [])

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

        {/* Topic Proficiency */}
        {user.topic_proficiency && Object.keys(user.topic_proficiency).length > 0 && (
          <div>
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
