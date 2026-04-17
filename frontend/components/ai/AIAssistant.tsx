import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, BookOpen, Target, MessageSquare, Sparkles, Globe, Copy, Share2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { useTranslation } from '@/components/ui/LanguageSelector'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Array<{
    type: string
    title: string
    url: string
    relevance: number
    metadata?: Record<string, any>
  }>
  confidence?: number
  copyText?: string
  shareUrl?: string
  aiSkillsUpdated?: boolean
}

interface Source {
  type: string
  id: string
  title: string
  content: string
  relevance: number
  url: string
}

export const AIAssistant: React.FC = () => {
  const { t, currentLang } = useTranslation()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [greeting, setGreeting] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Language-specific greeting messages for BIZIMANA FILS AI
  const greetings = {
    rw: 'Murakaza neza! Ndagira BIZIMANA FILS AI, umusizi wanyu wubaka imikino. Nshobora kugufasha iki cyangwa?',
    en: 'Welcome! I am BIZIMANA FILS AI, your sports assistant. How can I help you today?',
    fr: 'Bienvenue! Je suis BIZIMANA FILS AI, votre assistant sportif. Comment puis-je vous aider aujourd\'hui?',
    sw: 'Karibu! Mimi ni BIZIMANA FILS AI, msaidizi wako wa michezo. Ninaweza kukusaidia leo nini?'
  }

  // Language-specific placeholder texts
  const placeholders = {
    rw: 'Andika ikibazo cyangwa hano...',
    en: 'Type your question here...',
    fr: 'Tapez votre question ici...',
    sw: 'Andika swali lako hapa...'
  }

  // Language-specific typing indicators
  const typingIndicators = {
    rw: 'AI Assistant yarandika...',
    en: 'AI Assistant is typing...',
    fr: 'L\'assistant IA est en train d\'écrire...',
    sw: 'Msaidizi wa AI anaandika...'
  }

  useEffect(() => {
    // Set initial greeting based on current language
    setGreeting(greetings[currentLang as keyof typeof greetings] || greetings.en)
    
    // Load greeting from API
    fetchGreeting()
  }, [currentLang])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchGreeting = async () => {
    try {
      const response = await fetch(`/api/ai-assistant/greeting?language=${currentLang}`)
      const data = await response.json()
      if (data.greeting) {
        setGreeting(data.greeting)
      }
    } catch (error) {
      console.error('Failed to fetch greeting:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const generateMessageId = () => {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  const detectLanguage = (text: string) => {
    // Simple language detection based on common phrases
    const textLower = text.toLowerCase()
    
    if (textLower.includes('murakaza') || textLower.includes('amakuru') || 
        textLower.includes('ibibazo') || textLower.includes('nshobora')) {
      return 'rw'
    }
    if (textLower.includes('bonjour') || textLower.includes('aide') || 
        textLower.includes('questions') || textLower.includes('cours')) {
      return 'fr'
    }
    if (textLower.includes('karibu') || textLower.includes('msaada') || 
        textLower.includes('maswali') || textLower.includes('kozi')) {
      return 'sw'
    }
    
    return 'en' // Default to English
  }

  const formatSources = (sources: Source[]) => {
    return sources.map(source => ({
      type: source.type,
      title: source.title,
      url: source.url,
      relevance: source.relevance
    }))
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      // Show success feedback
      alert('BIZIMANA FILS AI: Response copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const shareResponse = async (shareUrl: string, text: string) => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: 'BIZIMANA FILS AI Response',
          text: text,
          url: shareUrl
        })
      } else {
        // Fallback: copy to clipboard
        await copyToClipboard(`BIZIMANA FILS AI: ${text}\n\nShare: ${shareUrl}`)
        alert('BIZIMANA FILS AI: Share link copied to clipboard!')
      }
    } catch (err) {
      console.error('Failed to share: ', err)
    }
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: generateMessageId(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)
    setIsTyping(true)

    try {
      const detectedLanguage = detectLanguage(inputValue)
      
      const response = await fetch('/api/ai-assistant/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue.trim(),
          language: detectedLanguage
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      const assistantMessage: Message = {
        id: generateMessageId(),
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        sources: formatSources(data.sources || []),
        confidence: data.confidence,
        copyText: data.copyText,
        shareUrl: data.shareUrl,
        aiSkillsUpdated: data.aiSkillsUpdated
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      const errorMessage: Message = {
        id: generateMessageId(),
        type: 'assistant',
        content: t('error_message', 'Sorry, I encountered an error. Please try again.'),
        timestamp: new Date(),
        confidence: 0
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setIsTyping(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'course':
        return <BookOpen className="w-4 h-4" />
      case 'task':
        return <Target className="w-4 h-4" />
      case 'post':
        return <MessageSquare className="w-4 h-4" />
      default:
        return <BookOpen className="w-4 h-4" />
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                BIZIMANA FILS AI
              </h2>
              <p className="text-gray-600">{greeting}</p>
            </div>
            <div className="flex items-center space-x-2">
              <Globe className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-500 uppercase">{currentLang}</span>
            </div>
          </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Sparkles className="w-12 h-12 text-primary-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {t('start_conversation', 'Start a conversation')}
            </h3>
            <p className="text-gray-600 max-w-md mx-auto">
              {t('assistant_help', 'I can help you with questions about courses, tasks, user data, and platform features. Ask me anything!')}
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-2xl ${
              message.type === 'user' 
                ? 'bg-primary-600 text-white' 
                : 'bg-white text-gray-900 border border-gray-200'
            } rounded-lg p-4 shadow-sm`}>
              <div className="flex items-start space-x-2">
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-primary-700' 
                    : 'bg-gray-100'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-gray-600" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="prose prose-sm max-w-none">
                    <p className="whitespace-pre-wrap break-words">
                      {message.content}
                    </p>
                  </div>
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-center space-x-2 mb-2">
                        <BookOpen className="w-4 h-4 text-gray-500" />
                        <span className="text-sm font-medium text-gray-700">
                          {t('sources', 'Sources')}
                        </span>
                        {message.confidence && (
                          <span className={`text-xs font-medium ${getConfidenceColor(message.confidence)}`}>
                            {Math.round(message.confidence * 100)}% confidence
                          </span>
                        )}
                      </div>
                      <div className="space-y-2">
                        {message.sources.slice(0, 3).map((source, index) => (
                          <a
                            key={index}
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-800 transition-colors"
                          >
                            {getSourceIcon(source.type)}
                            <span className="truncate">{source.title}</span>
                            <span className="text-xs text-gray-400">
                              ({Math.round(source.relevance * 100)}% relevant)
                            </span>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Timestamp */}
                  <div className={`text-xs mt-2 ${
                    message.type === 'user' ? 'text-primary-200' : 'text-gray-400'
                  }`}>
                    {formatTimestamp(message.timestamp)}
                  </div>
                  
                  {/* Copy and Share buttons for assistant messages */}
                  {message.type === 'assistant' && (
                    <div className="flex items-center space-x-2 mt-3">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => copyToClipboard(message.copyText || message.content)}
                        className="flex items-center space-x-1"
                      >
                        <Copy className="w-3 h-3" />
                        <span className="text-xs">Copy</span>
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => shareResponse(message.shareUrl || '', message.content)}
                        className="flex items-center space-x-1"
                      >
                        <Share2 className="w-3 h-3" />
                        <span className="text-xs">Share</span>
                      </Button>
                      {message.aiSkillsUpdated && (
                        <div className="flex items-center space-x-1 text-xs text-green-600">
                          <Sparkles className="w-3 h-3" />
                          <span>AI Skills Updated</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-900 border border-gray-200 rounded-lg p-4 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-gray-600" />
                </div>
                <div className="flex items-center space-x-1">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                  <span className="text-sm text-gray-500">
                    {typingIndicators[currentLang as keyof typeof typingIndicators] || typingIndicators.en}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <Input
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholders[currentLang as keyof typeof placeholders] || placeholders.en}
              disabled={isLoading}
              className="resize-none"
              rows={2}
              leftIcon={<MessageSquare className="w-4 h-4 text-gray-400" />}
            />
          </div>
          <Button
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim()}
            loading={isLoading}
            className="flex-shrink-0"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        
        {/* Quick Actions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setInputValue(t('help_courses', 'Help me find courses'))}
            disabled={isLoading}
          >
            <BookOpen className="w-3 h-3 mr-1" />
            {t('courses', 'Courses')}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setInputValue(t('help_tasks', 'Show me available tasks'))}
            disabled={isLoading}
          >
            <Target className="w-3 h-3 mr-1" />
            {t('tasks', 'Tasks')}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setInputValue(t('help_profile', 'How do I improve my profile?'))}
            disabled={isLoading}
          >
            <User className="w-3 h-3 mr-1" />
            {t('profile', 'Profile')}
          </Button>
        </div>
      </div>
    </div>
  )
}
