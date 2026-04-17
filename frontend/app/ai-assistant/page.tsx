'use client'

import React from 'react'
import { AIAssistant } from '@/components/ai/AIAssistant'

export default function AIAssistantPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            BIZIMANA FILS AI
          </h1>
          <p className="text-gray-600">
            Your intelligent sports assistant - Ask questions about courses, tasks, profile, and platform features. Get accurate answers using only app data with copy and share functionality.
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200" style={{ height: 'calc(100vh - 200px)' }}>
          <AIAssistant />
        </div>
      </div>
    </div>
  )
}
