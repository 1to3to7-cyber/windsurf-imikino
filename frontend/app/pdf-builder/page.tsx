'use client'

import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import axios from 'axios'

interface PDFSection {
  title: string
  content: string
  order: number
}

interface PDFTemplate {
  name: string
  description: string
  preview: string
}

interface PDFHistory {
  id: number
  title: string
  created_at: string
  status: string
  file_size: string
}

export default function PDFBuilder() {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [sections, setSections] = useState<PDFSection[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState('professional')
  const [style, setStyle] = useState('professional')
  const [aiEnhancement, setAiEnhancement] = useState(true)
  const [targetPlatform, setTargetPlatform] = useState('lovable')
  const [customPrompt, setCustomPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [templates, setTemplates] = useState<PDFTemplate[]>([])
  const [history, setHistory] = useState<PDFHistory[]>([])
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  const templates: PDFTemplate[] = [
    {
      name: 'professional',
      description: 'Clean, professional layout with headers',
      preview: '/templates/professional.png'
    },
    {
      name: 'academic',
      description: 'Academic format with citations',
      preview: '/templates/academic.png'
    },
    {
      name: 'creative',
      description: 'Creative layout with visual elements',
      preview: '/templates/creative.png'
    },
    {
      name: 'minimal',
      description: 'Clean, minimal layout',
      preview: '/templates/minimal.png'
    }
  ]

  const addSection = useCallback(() => {
    const newSection: PDFSection = {
      title: `Section ${sections.length + 1}`,
      content: '',
      order: sections.length
    }
    setSections([...sections, newSection])
  }, [sections])

  const removeSection = useCallback((index: number) => {
    setSections(sections.filter((_, i) => i !== index))
  }, [sections])

  const updateSection = useCallback((index: number, field: 'title' | 'content', value: string) => {
    const updatedSections = [...sections]
    updatedSections[index] = {
      ...updatedSections[index],
      [field]: value
    }
    setSections(updatedSections)
  }, [sections])

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadedFile(file)
    }
  }, [])

  const generatePDF = useCallback(async () => {
    if (!title.trim()) {
      alert('Please enter a title for your PDF')
      return
    }

    setIsGenerating(true)
    
    try {
      const response = await axios.post('/api/pdf/build-advanced', {
        title,
        sections,
        metadata: {
          author: 'Imikino User',
          created_at: new Date().toISOString(),
          language: 'en'
        },
        ai_enhancement: aiEnhancement,
        export_format: 'pdf',
        custom_prompt: customPrompt || undefined,
        target_platform: targetPlatform
      })

      if (response.data.pdf_content) {
        // Create download link
        const blob = new Blob([response.data.pdf_content], { type: 'application/pdf' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${title}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

        // Update history
        const newHistory: PDFHistory = {
          id: Date.now(),
          title,
          created_at: new Date().toISOString(),
          status: 'completed',
          file_size: '2.3 MB'
        }
        setHistory([newHistory, ...history])
      }

      // Handle platform-specific configs
      if (targetPlatform === 'lovable' && response.data.lovable_config) {
        console.log('Lovable config generated:', response.data.lovable_config)
      } else if (targetPlatform === 'aistudio' && response.data.aistudio_config) {
        console.log('AI Studio config generated:', response.data.aistudio_config)
      }

    } catch (error) {
      console.error('PDF generation failed:', error)
      alert('Failed to generate PDF. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }, [title, sections, aiEnhancement, customPrompt, targetPlatform, history])

  const uploadAndConvert = useCallback(async () => {
    if (!uploadedFile) {
      alert('Please select a file to upload')
      return
    }

    setIsGenerating(true)

    try {
      const formData = new FormData()
      formData.append('file', uploadedFile)

      const response = await axios.post('/api/pdf/upload-and-convert', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data) {
        // Create download link
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${uploadedFile.name.replace(/\.[^/.]+$/, '')}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }

    } catch (error) {
      console.error('File conversion failed:', error)
      alert('Failed to convert file. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }, [uploadedFile])

  // Load templates on mount
  useState(() => {
    setTemplates(templates)
    
    // Load PDF history
    const mockHistory: PDFHistory[] = [
      {
        id: 1,
        title: 'Project Proposal',
        created_at: '2026-04-17T10:30:00Z',
        status: 'completed',
        file_size: '2.3 MB'
      },
      {
        id: 2,
        title: 'Technical Documentation',
        created_at: '2026-04-17T09:15:00Z',
        status: 'completed',
        file_size: '1.8 MB'
      }
    ]
    setHistory(mockHistory)
  }, [])

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              AI-Powered PDF Builder
            </h1>
            <p className="text-gray-600 mb-8">
              Create professional PDFs with AI enhancement and export to Lovable, AI Studio, or download
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Basic Settings */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Document Settings
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Title
                    </label>
                    <Input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Enter document title..."
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Content
                    </label>
                    <textarea
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      placeholder="Enter your content here..."
                      className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* Sections */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Document Sections
                  </h2>
                  <Button
                    onClick={addSection}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                  >
                    Add Section
                  </Button>
                </div>

                <div className="space-y-4">
                  {sections.map((section, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <Input
                          type="text"
                          value={section.title}
                          onChange={(e) => updateSection(index, 'title', e.target.value)}
                          className="flex-1 mr-2"
                        />
                        <Button
                          onClick={() => removeSection(index)}
                          className="bg-red-600 text-white px-3 py-1 rounded-md hover:bg-red-700"
                        >
                          Remove
                        </Button>
                      </div>
                      <textarea
                        value={section.content}
                        onChange={(e) => updateSection(index, 'content', e.target.value)}
                        placeholder="Section content..."
                        className="w-full h-24 p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Template Selection */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Template & Style
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Template
                    </label>
                    <select
                      value={selectedTemplate}
                      onChange={(e) => setSelectedTemplate(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      {templates.map((template) => (
                        <option key={template.name} value={template.name}>
                          {template.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Style
                    </label>
                    <select
                      value={style}
                      onChange={(e) => setStyle(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="professional">Professional</option>
                      <option value="academic">Academic</option>
                      <option value="creative">Creative</option>
                      <option value="minimal">Minimal</option>
                    </select>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={aiEnhancement}
                      onChange={(e) => setAiEnhancement(e.target.checked)}
                      className="mr-2"
                    />
                    <label className="text-sm text-gray-700">
                      Enable AI Enhancement
                    </label>
                  </div>
                </div>
              </div>

              {/* Platform Integration */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  AI Platform Integration
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Export Platform
                    </label>
                    <select
                      value={targetPlatform}
                      onChange={(e) => setTargetPlatform(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="lovable">Lovable AI</option>
                      <option value="aistudio">AI Studio</option>
                      <option value="download">Direct Download</option>
                    </select>
                  </div>

                  {targetPlatform !== 'download' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Custom AI Prompt (Optional)
                      </label>
                      <textarea
                        value={customPrompt}
                        onChange={(e) => setCustomPrompt(e.target.value)}
                        placeholder="Enter custom AI enhancement prompt..."
                        className="w-full h-20 p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* File Upload */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  File Upload & Convert
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Upload File (.txt, .md, .docx, .html)
                    </label>
                    <input
                      type="file"
                      onChange={handleFileUpload}
                      accept=".txt,.md,.docx,.html"
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  {uploadedFile && (
                    <div className="mt-2 p-3 bg-gray-100 rounded-md">
                      <p className="text-sm text-gray-700">
                        Selected: {uploadedFile.name}
                      </p>
                    </div>
                  )}

                  <Button
                    onClick={uploadAndConvert}
                    disabled={!uploadedFile || isGenerating}
                    className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400"
                  >
                    {isGenerating ? (
                      <div className="flex items-center justify-center">
                        <LoadingSpinner size="small" />
                        <span className="ml-2">Converting...</span>
                      </div>
                    ) : (
                      'Upload & Convert to PDF'
                    )}
                  </Button>
                </div>
              </div>

              {/* Generate Button */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <Button
                  onClick={generatePDF}
                  disabled={!title.trim() || isGenerating}
                  className="w-full bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {isGenerating ? (
                    <div className="flex items-center justify-center">
                      <LoadingSpinner size="small" />
                      <span className="ml-2">Generating PDF...</span>
                    </div>
                  ) : (
                    'Generate Enhanced PDF'
                  )}
                </Button>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Template Preview */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Template Preview
                </h3>
                <div className="aspect-w-16 bg-gray-100 rounded-lg flex items-center justify-center">
                  <img
                    src={templates.find(t => t.name === selectedTemplate)?.preview || '/templates/default.png'}
                    alt={`${selectedTemplate} template preview`}
                    className="max-w-full max-h-full object-contain rounded-lg"
                  />
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {templates.find(t => t.name === selectedTemplate)?.description}
                </p>
              </div>

              {/* PDF History */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Recent PDFs
                </h3>
                <div className="space-y-3">
                  {history.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">
                      No PDFs generated yet
                    </p>
                  ) : (
                    history.map((item) => (
                      <div key={item.id} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">
                              {item.title}
                            </h4>
                            <p className="text-sm text-gray-600">
                              {item.created_at} • {item.file_size}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              item.status === 'completed' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {item.status}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* AI Features */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  AI Features
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M16.707 5.293a1 1 0 010-1.414 1.414l-8 8a1 1 0 00-1.414 1.414l8-8a1 1 0 001.414-1.414l8-8a1 1 0 011.414-1.414l-8 8a1 1 0 001.414 1.414z"/>
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h4 className="font-medium text-gray-900">AI Enhancement</h4>
                      <p className="text-sm text-gray-600">
                        Content is automatically enhanced with AI for better quality
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-blue-500 rounded-full flex items-center justify-center">
                      <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13 7H7v6h6v-6H7v6zm0 8v6h6v-6h-6v6z"/>
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h4 className="font-medium text-gray-900">Multi-Platform Export</h4>
                      <p className="text-sm text-gray-600">
                        Export to Lovable, AI Studio, or direct download
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-purple-500 rounded-full flex items-center justify-center">
                      <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 2a1 1 0 0002v14a1 1 0 002-2h6a1 1 0 002-2V2a2 2 0 00-2-2H6a2 2 0 00-2 2v14a2 2 0 002 2h6a2 2 0 002-2V2z"/>
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h4 className="font-medium text-gray-900">Professional Templates</h4>
                      <p className="text-sm text-gray-600">
                        Multiple professional templates available
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}
