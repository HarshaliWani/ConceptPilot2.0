'use client'

import React, { useState, useEffect } from 'react'
import { BookOpen, ChevronRight, ChevronLeft, GraduationCap, PlayCircle, ClipboardList } from 'lucide-react'

interface SubTopic {
  text: string
}

interface Module {
  moduleName: string
  subTopics: string[]
}

interface Subject {
  courseCode: string
  subjectName: string
  modules: Module[]
}

type View = 'subjects' | 'modules' | 'topics'

const ProgressTab: React.FC<{ onSectionChange?: (section: string) => void }> = ({ onSectionChange }) => {
  const [syllabus, setSyllabus] = useState<Subject[]>([])
  const [view, setView] = useState<View>('subjects')
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null)
  const [selectedModule, setSelectedModule] = useState<Module | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load syllabus from public folder
    fetch('/syllabus.json')
      .then(res => res.json())
      .then(data => {
        setSyllabus(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load syllabus:', err)
        setLoading(false)
      })
  }, [])

  const handleSubjectClick = (subject: Subject) => {
    setSelectedSubject(subject)
    setView('modules')
  }

  const handleModuleClick = (module: Module) => {
    setSelectedModule(module)
    setView('topics')
  }

  const handleBackToSubjects = () => {
    setSelectedSubject(null)
    setSelectedModule(null)
    setView('subjects')
  }

  const handleBackToModules = () => {
    setSelectedModule(null)
    setView('modules')
  }

  const handleStartLearning = (topic: string) => {
    // Switch to learning tab with pre-filled topic
    if (onSectionChange) {
      onSectionChange('learning')
      // Store topic in session storage for LearningDashboard to pick up
      sessionStorage.setItem('prefilled_topic', topic)
    }
  }

  const handleTakeQuiz = (topic: string) => {
    // Store topic and switch to quizzes tab — QuizzesTab will auto-generate
    sessionStorage.setItem('pending_quiz_topic', topic)
    if (onSectionChange) onSectionChange('quizzes')
  }

  const getSubjectColor = (index: number) => {
    const colors = [
      'from-blue-500 to-blue-600',
      'from-purple-500 to-purple-600',
      'from-green-500 to-green-600',
      'from-red-500 to-red-600',
      'from-yellow-500 to-yellow-600',
      'from-indigo-500 to-indigo-600',
      'from-pink-500 to-pink-600',
      'from-teal-500 to-teal-600',
    ]
    return colors[index % colors.length]
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  // Subjects View
  if (view === 'subjects') {
    return (
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Syllabus Dashboard</h1>
          <p className="text-gray-600">First Year Engineering - Explore subjects, modules, and topics</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {syllabus.map((subject, index) => (
            <button
              key={subject.courseCode}
              onClick={() => handleSubjectClick(subject)}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-all transform hover:-translate-y-1 text-left group"
            >
              <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${getSubjectColor(index)} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <BookOpen className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {subject.courseCode}
              </h3>
              <p className="text-sm text-gray-600 mb-3">{subject.subjectName}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">{subject.modules.length} modules</span>
                <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
              </div>
            </button>
          ))}
        </div>
      </div>
    )
  }

  // Modules View
  if (view === 'modules' && selectedSubject) {
    return (
      <div className="p-6">
        {/* Breadcrumb */}
        <div className="mb-6">
          <button
            onClick={handleBackToSubjects}
            className="flex items-center text-blue-600 hover:text-blue-700 mb-4"
          >
            <ChevronLeft className="w-5 h-5" />
            <span className="font-medium">Back to Subjects</span>
          </button>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            {selectedSubject.courseCode} - {selectedSubject.subjectName}
          </h1>
          <p className="text-gray-600">{selectedSubject.modules.length} modules available</p>
        </div>

        <div className="space-y-4">
          {selectedSubject.modules.map((module, index) => (
            <button
              key={index}
              onClick={() => handleModuleClick(module)}
              className="w-full bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all text-left group"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                      <GraduationCap className="w-5 h-5 text-blue-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900">{module.moduleName}</h3>
                  </div>
                  <p className="text-sm text-gray-500 ml-13">{module.subTopics.length} subtopics</p>
                </div>
                <ChevronRight className="w-6 h-6 text-gray-400 group-hover:text-blue-500 transition-colors" />
              </div>
            </button>
          ))}
        </div>
      </div>
    )
  }

  // Topics View
  if (view === 'topics' && selectedSubject && selectedModule) {
    return (
      <div className="p-6">
        {/* Breadcrumb */}
        <div className="mb-6">
          <button
            onClick={handleBackToModules}
            className="flex items-center text-blue-600 hover:text-blue-700 mb-4"
          >
            <ChevronLeft className="w-5 h-5" />
            <span className="font-medium">Back to Modules</span>
          </button>
          <div className="text-sm text-gray-500 mb-2">
            {selectedSubject.courseCode} {'>'} {selectedModule.moduleName}
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">{selectedModule.moduleName}</h1>
          <p className="text-gray-600">Choose a subtopic to start learning or take a quiz</p>
        </div>

        <div className="space-y-4">
          {selectedModule.subTopics.map((topic, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <p className="text-gray-800 mb-4 leading-relaxed">{topic}</p>
              <div className="flex space-x-3">
                <button
                  onClick={() => handleStartLearning(topic)}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <PlayCircle className="w-5 h-5" />
                  <span>Start Learning</span>
                </button>
                <button
                  onClick={() => handleTakeQuiz(topic)}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <ClipboardList className="w-5 h-5" />
                  <span>Take Quiz</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return null
}

export default ProgressTab