'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/Button'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { useTranslation } from '@/components/ui/LanguageSelector'
import { 
  FileText, 
  Folder, 
  Database, 
  Cloud, 
  Terminal, 
  Download, 
  Upload, 
  Save, 
  Play, 
  Settings, 
  Monitor,
  Code,
  Shield,
  GitBranch,
  Activity,
  HardDrive,
  Trash2,
  Copy,
  Move,
  Plus,
  X,
  Check,
  AlertTriangle,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  Search,
  Edit3,
  Eye,
  EyeOff,
  Zap,
  Clock,
  Server,
  Package,
  BarChart3,
  Users,
  File
} from 'lucide-react'

interface FileNode {
  name: string
  type: 'file' | 'directory'
  path: string
  size?: number
  modified?: string
  children?: FileNode[]
  content?: string
  syntax?: string
}

interface SQLQueryResult {
  columns: string[]
  data: any[]
  rowCount: number
}

interface Deployment {
  id: string
  platform: string
  environment: string
  status: string
  progress: number
  logs: string[]
  startedAt: string
}

interface ProjectStatus {
  system: {
    uptime: string
    cpuUsage: number
    memoryUsage: number
    diskUsage: number
  }
  services: {
    frontend: string
    backend: string
    database: string
  }
  statistics: {
    totalFiles: number
    projectSize: number
    databaseSize: number
  }
}

export default function AdminChamberPage() {
  const { t, currentLang } = useTranslation()
  const [activeTab, setActiveTab] = useState<'files' | 'database' | 'deployment' | 'status'>('files')
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<string>('')
  const [fileSyntax, setFileSyntax] = useState<string>('text')
  const [isLoading, setIsLoading] = useState(false)
  const [projectStructure, setProjectStructure] = useState<FileNode | null>(null)
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
  const [sqlQuery, setSqlQuery] = useState<string>('')
  const [sqlResults, setSqlResults] = useState<SQLQueryResult | null>(null)
  const [deployments, setDeployments] = useState<Deployment[]>([])
  const [projectStatus, setProjectStatus] = useState<ProjectStatus | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')
  const [editorTheme, setEditorTheme] = useState('vs-dark')
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<string>('')
  
  const editorRef = useRef<any>(null)

  useEffect(() => {
    // Load Monaco Editor dynamically
    if (typeof window !== 'undefined') {
      import('@monaco-editor/react').then((monaco) => {
        // Monaco is loaded
      })
    }
  }, [])

  useEffect(() => {
    // Set editor theme based on overall theme
    setEditorTheme(theme === 'dark' ? 'vs-dark' : 'vs')
  }, [theme])

  const loadProjectStructure = async () => {
    try {
      const response = await fetch('/api/admin/chamber/project-structure')
      const data = await response.json()
      setProjectStructure(data)
    } catch (error) {
      console.error('Failed to load project structure:', error)
    }
  }

  const loadFileContent = async (filePath: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(`/api/admin/chamber/file/${encodeURIComponent(filePath)}`)
      const data = await response.json()
      setFileContent(data.content)
      setFileSyntax(data.syntax)
      setSelectedFile(filePath)
    } catch (error) {
      console.error('Failed to load file content:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const saveFile = async (content: string) => {
    if (!selectedFile) return
    
    setIsSaving(true)
    try {
      const response = await fetch('/api/admin/chamber/file/edit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_path: selectedFile,
          content: content,
          encoding: 'utf-8'
        })
      })
      
      if (response.ok) {
        setLastSaved(new Date().toLocaleTimeString())
        // Show success notification
      }
    } catch (error) {
      console.error('Failed to save file:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const executeSQLQuery = async () => {
    if (!sqlQuery.trim()) return
    
    setIsLoading(true)
    try {
      const response = await fetch('/api/admin/chamber/database/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: sqlQuery,
          database: 'imikino.db'
        })
      })
      
      const data = await response.json()
      setSqlResults(data)
    } catch (error) {
      console.error('Failed to execute SQL query:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const deployProject = async (platform: string) => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/admin/chamber/deployment/deploy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platform,
          environment: 'production'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setDeployments(prev => [data, ...prev])
      }
    } catch (error) {
      console.error('Failed to deploy:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const downloadProject = async () => {
    try {
      const response = await fetch('/api/admin/chamber/download/project')
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `imikino_project_${new Date().toISOString().split('T')[0]}.zip`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Failed to download project:', error)
    }
  }

  const renderFileTree = (node: FileNode, level: number = 0): JSX.Element => {
    const isExpanded = expandedFolders.has(node.path)
    const indent = level * 20

    return (
      <div key={node.path} className="select-none">
        <div 
          className="flex items-center py-1 px-2 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer rounded"
          style={{ paddingLeft: `${indent}px` }}
          onClick={() => {
            if (node.type === 'directory') {
              setExpandedFolders(prev => {
                const newSet = new Set(prev)
                if (newSet.has(node.path)) {
                  newSet.delete(node.path)
                } else {
                  newSet.add(node.path)
                }
                return newSet
              })
            } else {
              loadFileContent(node.path)
            }
          }}
        >
          {node.type === 'directory' ? (
            <ChevronRight 
              className={`w-4 h-4 mr-2 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
            />
          ) : (
            <FileText className="w-4 h-4 mr-2 text-blue-500" />
          )}
          <span className="text-sm font-medium">{node.name}</span>
          {node.size && (
            <span className="ml-2 text-xs text-gray-500">
              {(node.size / 1024).toFixed(1)}KB
            </span>
          )}
        </div>
        {node.type === 'directory' && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderFileTree(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  const MonacoEditor = () => {
    if (typeof window === 'undefined') return <div>Loading editor...</div>
    
    return (
      <div className="h-full border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
        <div className="bg-gray-50 dark:bg-gray-900 px-4 py-2 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <FileText className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
              {selectedFile || 'Untitled'}
            </span>
            {lastSaved && (
              <span className="text-xs text-green-600">
                Saved at {lastSaved}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              disabled={!selectedFile || isSaving}
              onClick={() => saveFile(fileContent)}
            >
              {isSaving ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Save className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
        <div className="h-full">
          <textarea
            ref={editorRef}
            value={fileContent}
            onChange={(e) => setFileContent(e.target.value)}
            className="w-full h-full p-4 font-mono text-sm bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 resize-none focus:outline-none"
            style={{
              fontFamily: 'Monaco, Consolas, "Courier New", monospace',
              tabSize: 2,
              lineHeight: 1.5
            }}
            placeholder="Select a file to edit..."
            spellCheck={false}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <Shield className="w-6 h-6 text-blue-600" />
              <div>
                <h1 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  Admin Chamber
                </h1>
                <p className="text-xs text-gray-500">
                  1to3to7@gmail.com
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto">
            <nav className="p-2 space-y-1">
              <button
                onClick={() => setActiveTab('files')}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeTab === 'files'
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                <Folder className="w-4 h-4" />
                <span className="text-sm font-medium">File Manager</span>
              </button>
              
              <button
                onClick={() => setActiveTab('database')}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeTab === 'database'
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                <Database className="w-4 h-4" />
                <span className="text-sm font-medium">Database Admin</span>
              </button>
              
              <button
                onClick={() => setActiveTab('deployment')}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeTab === 'deployment'
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                <Cloud className="w-4 h-4" />
                <span className="text-sm font-medium">Deployment</span>
              </button>
              
              <button
                onClick={() => setActiveTab('status')}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeTab === 'status'
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                <Monitor className="w-4 h-4" />
                <span className="text-sm font-medium">Project Status</span>
              </button>
            </nav>
          </div>

          {/* Quick Actions */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={downloadProject}
                disabled={isLoading}
              >
                <Download className="w-4 h-4 mr-2" />
                Download Project
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={loadProjectStructure}
                disabled={isLoading}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Files
              </Button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {activeTab === 'files' && (
            <div className="flex-1 flex">
              {/* File Tree */}
              <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
                <div className="p-4">
                  <div className="mb-4">
                    <div className="relative">
                      <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search files..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100"
                      />
                    </div>
                  </div>
                  
                  {projectStructure && (
                    <div className="space-y-1">
                      <div className="mb-2">
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">Frontend</h3>
                        {renderFileTree(projectStructure.frontend)}
                      </div>
                      <div className="mb-2">
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">Backend</h3>
                        {renderFileTree(projectStructure.backend)}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Code Editor */}
              <div className="flex-1">
                <MonacoEditor />
              </div>
            </div>
          )}

          {activeTab === 'database' && (
            <div className="flex-1 p-6">
              <div className="max-w-4xl mx-auto">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
                  Database Administration
                </h2>
                
                {/* SQL Query Editor */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                    SQL Query Editor
                  </h3>
                  <textarea
                    value={sqlQuery}
                    onChange={(e) => setSqlQuery(e.target.value)}
                    placeholder="Enter SELECT query here..."
                    className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100"
                    spellCheck={false}
                  />
                  <div className="mt-4 flex items-center space-x-4">
                    <Button
                      onClick={executeSQLQuery}
                      disabled={!sqlQuery.trim() || isLoading}
                      className="flex items-center space-x-2"
                    >
                      {isLoading ? <LoadingSpinner size="sm" /> : <Play className="w-4 h-4" />}
                      Execute Query
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setSqlResults(null)}
                    >
                      <X className="w-4 h-4" />
                      Clear
                    </Button>
                  </div>
                </div>

                {/* Results */}
                {sqlResults && (
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                      Query Results ({sqlResults.rowCount} rows)
                    </h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            {sqlResults.columns.map(column => (
                              <th key={column} className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                {column}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {sqlResults.data.map((row, index) => (
                            <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                              {sqlResults.columns.map(column => (
                                <td key={column} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                  {row[column]?.toString() || '-'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'deployment' && (
            <div className="flex-1 p-6">
              <div className="max-w-4xl mx-auto">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
                  Deployment Controls
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <Button
                    onClick={() => deployProject('vercel')}
                    disabled={isLoading}
                    className="flex items-center space-x-2 h-16"
                  >
                    <Package className="w-6 h-6" />
                    <div className="text-left">
                      <div className="font-semibold">Deploy to Vercel</div>
                      <div className="text-sm text-gray-500">Production deployment</div>
                    </div>
                  </Button>
                  
                  <Button
                    onClick={() => deployProject('render')}
                    disabled={isLoading}
                    className="flex items-center space-x-2 h-16"
                  >
                    <Server className="w-6 h-6" />
                    <div className="text-left">
                      <div className="font-semibold">Deploy to Render</div>
                      <div className="text-sm text-gray-500">Production deployment</div>
                    </div>
                  </Button>
                </div>

                {/* Deployment History */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                    Deployment History
                  </h3>
                  <div className="space-y-4">
                    {deployments.map(deployment => (
                      <div key={deployment.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <Package className="w-4 h-4 text-blue-600" />
                            <span className="font-medium">{deployment.platform}</span>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            deployment.status === 'completed' ? 'bg-green-100 text-green-800' :
                            deployment.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {deployment.status}
                          </span>
                        </div>
                        <div className="mb-2">
                          <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                            <span>Environment: {deployment.environment}</span>
                            <span>Started: {new Date(deployment.startedAt).toLocaleString()}</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${deployment.progress}%` }}
                            />
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {deployment.logs.map((log, index) => (
                            <div key={index} className="mb-1">{log}</div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'status' && (
            <div className="flex-1 p-6">
              <div className="max-w-6xl mx-auto">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
                  Project Status & Monitoring
                </h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* System Status */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                    <div className="flex items-center space-x-3 mb-4">
                      <Server className="w-6 h-6 text-green-600" />
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        System Status
                      </h3>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Uptime</span>
                        <span className="text-sm font-medium">{projectStatus?.system?.uptime || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">CPU Usage</span>
                        <span className="text-sm font-medium">{projectStatus?.system?.cpuUsage || 0}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Memory Usage</span>
                        <span className="text-sm font-medium">{projectStatus?.system?.memoryUsage || 0}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Disk Usage</span>
                        <span className="text-sm font-medium">{projectStatus?.system?.diskUsage || 0}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Services Status */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                    <div className="flex items-center space-x-3 mb-4">
                      <Activity className="w-6 h-6 text-blue-600" />
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        Services Status
                      </h3>
                    </div>
                    <div className="space-y-3">
                      {projectStatus?.services && Object.entries(projectStatus.services).map(([service, status]) => (
                        <div key={service} className="flex justify-between">
                          <span className="text-sm text-gray-600 capitalize">{service}</span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            status === 'running' ? 'bg-green-100 text-green-800' :
                            status === 'stopped' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Statistics */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                    <div className="flex items-center space-x-3 mb-4">
                      <BarChart3 className="w-6 h-6 text-purple-600" />
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        Project Statistics
                      </h3>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Total Files</span>
                        <span className="text-sm font-medium">{projectStatus?.statistics?.totalFiles || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Project Size</span>
                        <span className="text-sm font-medium">{(projectStatus?.statistics?.projectSize / 1024 / 1024).toFixed(1)}MB</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Database Size</span>
                        <span className="text-sm font-medium">{(projectStatus?.statistics?.databaseSize / 1024).toFixed(1)}KB</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
