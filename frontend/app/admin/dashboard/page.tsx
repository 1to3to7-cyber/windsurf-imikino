import React, { useState, useEffect } from 'react'
import { Users, CheckCircle, XCircle, Clock, Download, TrendingUp, Eye, MessageSquare, BookOpen, Target } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'

interface DashboardStats {
  total_users: number
  active_users: number
  total_posts: number
  pending_posts: number
  total_courses: number
  active_courses: number
  total_tasks: number
  pending_tasks: number
  total_submissions: number
  pending_submissions: number
}

interface User {
  id: number
  email: string
  display_name: string
  role: string
  is_active: boolean
  created_at: string
  last_login?: string
  xp_points: number
  level: number
}

interface Post {
  id: number
  title: string
  content: string
  author_name: string
  status: string
  created_at: string
  likes_count: number
  comments_count: number
}

interface Task {
  id: number
  title: string
  description: string
  xp_reward: number
  status: string
  priority: string
  created_at: string
  submissions_count: number
}

interface Submission {
  id: number
  task_title: string
  user_name: string
  proof: string
  status: string
  submitted_at: string
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [posts, setPosts] = useState<Post[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch dashboard stats
      const statsResponse = await fetch('/api/admin/dashboard/stats')
      const statsData = await statsResponse.json()
      setStats(statsData.data)
      
      // Fetch recent users
      const usersResponse = await fetch('/api/admin/users?limit=10')
      const usersData = await usersResponse.json()
      setUsers(usersData.data.users)
      
      // Fetch pending posts
      const postsResponse = await fetch('/api/admin/posts?status=pending&limit=10')
      const postsData = await postsResponse.json()
      setPosts(postsData.data.posts)
      
      // Fetch pending tasks
      const tasksResponse = await fetch('/api/admin/tasks?status=pending&limit=10')
      const tasksData = await tasksResponse.json()
      setTasks(tasksData.data.tasks)
      
      // Fetch pending submissions
      const submissionsResponse = await fetch('/api/admin/submissions?status=pending&limit=10')
      const submissionsData = await submissionsResponse.json()
      setSubmissions(submissionsData.data.submissions)
      
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUserAction = async (userId: number, action: string) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (response.ok) {
        fetchDashboardData() // Refresh data
      }
    } catch (error) {
      console.error(`Failed to ${action} user:`, error)
    }
  }

  const handlePostModeration = async (postId: number, action: string) => {
    try {
      const response = await fetch(`/api/admin/posts/${postId}/moderate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action })
      })
      
      if (response.ok) {
        fetchDashboardData() // Refresh data
      }
    } catch (error) {
      console.error(`Failed to ${action} post:`, error)
    }
  }

  const handleTaskApproval = async (taskId: number, action: string) => {
    try {
      const response = await fetch(`/api/admin/tasks/${taskId}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (response.ok) {
        fetchDashboardData() // Refresh data
      }
    } catch (error) {
      console.error(`Failed to ${action} task:`, error)
    }
  }

  const handleSubmissionReview = async (submissionId: number, action: string, feedback?: string) => {
    try {
      const response = await fetch(`/api/admin/submissions/${submissionId}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action, feedback })
      })
      
      if (response.ok) {
        fetchDashboardData() // Refresh data
      }
    } catch (error) {
      console.error(`Failed to ${action} submission:`, error)
    }
  }

  const exportToCSV = async (dataType: string) => {
    try {
      const response = await fetch(`/api/admin/export/${dataType}`)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${dataType}_export_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error(`Failed to export ${dataType}:`, error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Admin Dashboard
          </h1>
          <p className="text-gray-600">
            Manage users, content, and monitor platform activity
          </p>
        </div>

        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Users</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-green-100 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Users</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.active_users}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <MessageSquare className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Posts</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_posts}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <Clock className="h-6 w-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Pending Posts</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.pending_posts}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-indigo-100 rounded-lg">
                  <BookOpen className="h-6 w-6 text-indigo-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Courses</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_courses}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-red-100 rounded-lg">
                  <Target className="h-6 w-6 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Tasks</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_tasks}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-3 bg-orange-100 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Pending Tasks</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.pending_tasks}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Export Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Export Data</h2>
          <div className="flex flex-wrap gap-4">
            <Button
              variant="secondary"
              onClick={() => exportToCSV('users')}
              className="flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Users
            </Button>
            <Button
              variant="secondary"
              onClick={() => exportToCSV('posts')}
              className="flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Posts
            </Button>
            <Button
              variant="secondary"
              onClick={() => exportToCSV('courses')}
              className="flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Courses
            </Button>
            <Button
              variant="secondary"
              onClick={() => exportToCSV('tasks')}
              className="flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Tasks
            </Button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {['overview', 'users', 'posts', 'tasks', 'submissions'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow">
          {activeTab === 'users' && (
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Users</h2>
              {users.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Role
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          XP/Level
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{user.display_name}</div>
                              <div className="text-sm text-gray-500">{user.email}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              user.role === 'admin' 
                                ? 'bg-purple-100 text-purple-800'
                                : 'bg-green-100 text-green-800'
                            }`}>
                              {user.role}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              user.is_active
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.xp_points} / Level {user.level}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex space-x-2">
                              {user.role !== 'admin' && (
                                <Button
                                  size="sm"
                                  variant="secondary"
                                  onClick={() => handleUserAction(user.id, 'promote')}
                                >
                                  Promote
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant={user.is_active ? 'danger' : 'primary'}
                                onClick={() => handleUserAction(user.id, user.is_active ? 'deactivate' : 'activate')}
                              >
                                {user.is_active ? 'Deactivate' : 'Activate'}
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <EmptyState
                  icon={<Users />}
                  title="No users found"
                  description="No users have registered yet."
                />
              )}
            </div>
          )}

          {activeTab === 'posts' && (
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Pending Posts</h2>
              {posts.length > 0 ? (
                <div className="space-y-4">
                  {posts.map((post) => (
                    <div key={post.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-medium text-gray-900">{post.title}</h3>
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          post.status === 'pending'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {post.status}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">{post.content}</p>
                      <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                        <span>By {post.author_name}</span>
                        <span>{new Date(post.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <div className="flex space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Eye className="w-4 h-4 mr-1" />
                            {post.likes_count} likes
                          </span>
                          <span className="flex items-center">
                            <MessageSquare className="w-4 h-4 mr-1" />
                            {post.comments_count} comments
                          </span>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => handlePostModeration(post.id, 'approve')}
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="danger"
                            onClick={() => handlePostModeration(post.id, 'reject')}
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            Reject
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={<MessageSquare />}
                  title="No pending posts"
                  description="All posts have been reviewed."
                />
              )}
            </div>
          )}

          {activeTab === 'tasks' && (
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Pending Tasks</h2>
              {tasks.length > 0 ? (
                <div className="space-y-4">
                  {tasks.map((task) => (
                    <div key={task.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-medium text-gray-900">{task.title}</h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            task.priority === 'high'
                              ? 'bg-red-100 text-red-800'
                              : task.priority === 'medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {task.priority}
                          </span>
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            task.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {task.status}
                          </span>
                        </div>
                      </div>
                      <p className="text-gray-600 mb-3">{task.description}</p>
                      <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                        <span>{task.submissions_count} submissions</span>
                        <span>{task.xp_reward} XP reward</span>
                        <span>{new Date(task.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => handleTaskApproval(task.id, 'approve')}
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleTaskApproval(task.id, 'reject')}
                        >
                          <XCircle className="w-4 h-4 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={<Target />}
                  title="No pending tasks"
                  description="All tasks have been reviewed."
                />
              )}
            </div>
          )}

          {activeTab === 'submissions' && (
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Pending Submissions</h2>
              {submissions.length > 0 ? (
                <div className="space-y-4">
                  {submissions.map((submission) => (
                    <div key={submission.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-medium text-gray-900">{submission.task_title}</h3>
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          submission.status === 'pending'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {submission.status}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">{submission.proof}</p>
                      <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                        <span>By {submission.user_name}</span>
                        <span>{new Date(submission.submitted_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => handleSubmissionReview(submission.id, 'approve', 'Great work! Task completed successfully.')}
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleSubmissionReview(submission.id, 'reject', 'Please provide more detailed proof or complete the task requirements.')}
                        >
                          <XCircle className="w-4 h-4 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={<Target />}
                  title="No pending submissions"
                  description="All submissions have been reviewed."
                />
              )}
            </div>
          )}

          {activeTab === 'overview' && (
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Platform Overview</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-md font-medium text-gray-900">Recent Activity</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-sm text-gray-600">New users today</span>
                      <span className="text-sm font-medium text-gray-900">12</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-sm text-gray-600">Posts created today</span>
                      <span className="text-sm font-medium text-gray-900">8</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-sm text-gray-600">Tasks completed today</span>
                      <span className="text-sm font-medium text-gray-900">15</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-sm text-gray-600">Course enrollments today</span>
                      <span className="text-sm font-medium text-gray-900">23</span>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <h3 className="text-md font-medium text-gray-900">System Health</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-sm text-gray-600">Database status</span>
                      <span className="text-sm font-medium text-green-600">Healthy</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-sm text-gray-600">API response time</span>
                      <span className="text-sm font-medium text-green-600">142ms</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-sm text-gray-600">Error rate</span>
                      <span className="text-sm font-medium text-green-600">0.2%</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-sm text-gray-600">Uptime</span>
                      <span className="text-sm font-medium text-green-600">99.9%</span>
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
