'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { AdminStats, Submission, Post, User } from '@/types';
import { useRouter } from 'next/navigation';

export default function AdminPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'submissions' | 'posts' | 'users' | 'stats'>('submissions');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      if (user.role !== 'admin') {
        router.push('/');
        return;
      }
      loadAdminData();
    }
  }, [user]);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      const [statsData, submissionsData, postsData, usersData] = await Promise.all([
        apiClient.getAdminStats(),
        apiClient.getAdminSubmissions(),
        apiClient.getAdminPosts(),
        apiClient.getAdminUsers()
      ]);
      setStats(statsData);
      setSubmissions(submissionsData);
      setPosts(postsData);
      setUsers(usersData);
    } catch (err: any) {
      setError(err.message || 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const moderateSubmission = async (submissionId: number, action: 'approve' | 'reject') => {
    try {
      setSubmitting(true);
      await apiClient.moderateSubmission(submissionId, action);
      // Reload data
      await loadAdminData();
    } catch (err: any) {
      setError(err.message || 'Failed to moderate submission');
    } finally {
      setSubmitting(false);
    }
  };

  const moderatePost = async (postId: number, action: 'approve' | 'reject') => {
    try {
      setSubmitting(true);
      await apiClient.moderatePost(postId, action);
      // Reload data
      await loadAdminData();
    } catch (err: any) {
      setError(err.message || 'Failed to moderate post');
    } finally {
      setSubmitting(false);
    }
  };

  const toggleUserRole = async (userId: number, newRole: 'admin' | 'member') => {
    try {
      setSubmitting(true);
      await apiClient.updateUserRole(userId, newRole);
      // Reload data
      await loadAdminData();
    } catch (err: any) {
      setError(err.message || 'Failed to update user role');
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to access admin panel</p>
          <button onClick={() => router.push('/login')} className="btn btn-primary">
            Sign In
          </button>
        </div>
      </div>
    );
  }

  if (user.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Access denied. Admin privileges required.</p>
          <button onClick={() => router.push('/')} className="btn btn-primary">
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container-mobile py-4">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => router.push('/')} 
              className="text-xl font-bold text-gray-900"
            >
              ← Back to Home
            </button>
            <h1 className="text-xl font-bold text-gray-900">Admin Panel</h1>
            <div className="w-6"></div>
          </div>
        </div>
      </header>

      <div className="container-mobile py-6">
        {/* Error Message */}
        {error && (
          <div className="bg-error-50 border border-error-200 text-error-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('submissions')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'submissions'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Submissions
          </button>
          <button
            onClick={() => setActiveTab('posts')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'posts'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Posts
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'users'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Users
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'stats'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Stats
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'submissions' && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-gray-900">Pending Submissions</h2>
            {submissions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No pending submissions</p>
              </div>
            ) : (
              submissions.map((submission) => (
                <div key={submission.id} className="card">
                  <div className="card-body">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{submission.task_title}</h3>
                        <p className="text-sm text-gray-600">By: {submission.user_display_name}</p>
                        <p className="text-xs text-gray-500">
                          Submitted: {new Date(submission.submitted_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className={`badge badge-${
                        submission.status === 'pending' ? 'warning' :
                        submission.status === 'approved' ? 'success' : 'error'
                      }`}>
                        {submission.status}
                      </span>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-3 mb-4">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {submission.proof_content}
                      </p>
                    </div>

                    {submission.status === 'pending' && (
                      <div className="flex space-x-3">
                        <button
                          onClick={() => moderateSubmission(submission.id, 'approve')}
                          className="btn btn-success"
                          disabled={submitting}
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => moderateSubmission(submission.id, 'reject')}
                          className="btn btn-error"
                          disabled={submitting}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'posts' && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-gray-900">Post Moderation</h2>
            {posts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No posts pending moderation</p>
              </div>
            ) : (
              posts.map((post) => (
                <div key={post.id} className="card">
                  <div className="card-body">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{post.display_name}</h3>
                        <p className="text-xs text-gray-500">
                          Posted: {new Date(post.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className={`badge badge-${
                        post.status === 'pending' ? 'warning' :
                        post.status === 'approved' ? 'success' : 'error'
                      }`}>
                        {post.status}
                      </span>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-3 mb-4">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {post.content}
                      </p>
                    </div>

                    {post.status === 'pending' && (
                      <div className="flex space-x-3">
                        <button
                          onClick={() => moderatePost(post.id, 'approve')}
                          className="btn btn-success"
                          disabled={submitting}
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => moderatePost(post.id, 'reject')}
                          className="btn btn-error"
                          disabled={submitting}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-gray-900">User Management</h2>
            {users.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No users found</p>
              </div>
            ) : (
              users.map((user_item) => (
                <div key={user_item.id} className="card">
                  <div className="card-body">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">{user_item.display_name}</h3>
                        <p className="text-sm text-gray-600">{user_item.email}</p>
                        <p className="text-xs text-gray-500">
                          Joined: {new Date(user_item.created_at).toLocaleDateString()}
                        </p>
                        <p className="text-sm text-primary-600 font-medium">
                          {user_item.xp} XP
                        </p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`badge badge-${
                          user_item.role === 'admin' ? 'primary' : 'secondary'
                        }`}>
                          {user_item.role}
                        </span>
                        {user_item.id !== user.id && (
                          <button
                            onClick={() => toggleUserRole(
                              user_item.id, 
                              user_item.role === 'admin' ? 'member' : 'admin'
                            )}
                            className="btn btn-secondary"
                            disabled={submitting}
                          >
                            {user_item.role === 'admin' ? 'Remove Admin' : 'Make Admin'}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'stats' && stats && (
          <div className="space-y-6">
            <h2 className="text-lg font-bold text-gray-900">Platform Statistics</h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Total Posts</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_posts}</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Pending Submissions</p>
                <p className="text-2xl font-bold text-warning-600">{stats.pending_submissions}</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Pending Posts</p>
                <p className="text-2xl font-bold text-warning-600">{stats.pending_posts}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Total Courses</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_courses}</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Total Tasks</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_tasks}</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Admin Users</p>
                <p className="text-2xl font-bold text-primary-600">{stats.admin_users}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
