'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { User, UserProgress, BADGES } from '@/types';
import Link from 'next/link';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const [userProgress, setUserProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    display_name: '',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadUserProgress();
      setEditForm({ display_name: user.display_name });
    }
  }, [user]);

  const loadUserProgress = async () => {
    try {
      const progress = await apiClient.getUserProgress();
      setUserProgress(progress);
    } catch (err: any) {
      setError(err.message || 'Failed to load progress');
    } finally {
      setLoading(false);
    }
  };

  const handleEditProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!editForm.display_name.trim()) {
      setError('Display name cannot be empty');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      // Note: In a real app, you'd have an API endpoint to update profile
      // For now, we'll just show the edit form
      setEditing(false);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to view your profile</p>
          <Link href="/login" className="btn btn-primary">
            Sign In
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
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
            <Link href="/" className="text-xl font-bold text-gray-900">
              ← Back to Home
            </Link>
            <button
              onClick={logout}
              className="btn btn-secondary"
            >
              Sign Out
            </button>
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

        {/* Profile Card */}
        <div className="card mb-6">
          <div className="card-body">
            <div className="flex items-center mb-6">
              <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mr-4">
                <span className="text-primary-600 text-2xl font-bold">
                  {user.display_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-gray-900">{user.display_name}</h1>
                <p className="text-gray-600">{user.email}</p>
                <div className="flex items-center mt-2">
                  <span className="badge badge-primary mr-2">
                    {user.role === 'admin' ? 'Admin' : 'Member'}
                  </span>
                  <span className="text-sm text-gray-500">
                    Member since {new Date(user.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            {/* XP Display */}
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg p-4 text-white mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-primary-100 text-sm">Total XP</p>
                  <p className="text-3xl font-bold">{user.xp}</p>
                </div>
                <div className="text-4xl">⭐</div>
              </div>
            </div>

            {/* Edit Profile Form */}
            {editing ? (
              <form onSubmit={handleEditProfile} className="space-y-4">
                <div>
                  <label htmlFor="display_name" className="form-label">
                    Display Name
                  </label>
                  <input
                    id="display_name"
                    name="display_name"
                    type="text"
                    className="form-input"
                    value={editForm.display_name}
                    onChange={(e) => setEditForm({ ...editForm, display_name: e.target.value })}
                    disabled={saving}
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditing(false)}
                    className="btn btn-secondary"
                    disabled={saving}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <button
                onClick={() => setEditing(true)}
                className="btn btn-secondary"
              >
                Edit Profile
              </button>
            )}
          </div>
        </div>

        {/* Badges Section */}
        <div className="card mb-6">
          <div className="card-body">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Badges</h2>
            {user.badges.length === 0 ? (
              <p className="text-gray-500">No badges earned yet. Start learning to earn badges!</p>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {user.badges.map((badgeId) => {
                  const badge = BADGES.find(b => b.id === badgeId);
                  if (!badge) return null;
                  return (
                    <div key={badge.id} className="text-center">
                      <div className="text-4xl mb-2">{badge.icon}</div>
                      <h3 className="font-medium text-gray-900">{badge.name}</h3>
                      <p className="text-sm text-gray-600">{badge.description}</p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Progress Section */}
        {userProgress && (
          <div className="card">
            <div className="card-body">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Learning Progress</h2>
              <div className="space-y-4">
                <div className="bg-success-50 border border-success-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-success-800 font-medium">Courses Completed</p>
                      <p className="text-2xl font-bold text-success-900">
                        {userProgress.total_courses_completed}
                      </p>
                    </div>
                    <div className="text-3xl">🎓</div>
                  </div>
                </div>

                {userProgress.progress.length === 0 ? (
                  <p className="text-gray-500">No progress yet. Start a course to begin learning!</p>
                ) : (
                  <div className="space-y-3">
                    <h3 className="font-medium text-gray-900">Recent Activity</h3>
                    {userProgress.progress.slice(0, 5).map((item, index) => (
                      <div key={index} className="flex items-center justify-between py-2 border-b border-gray-200 last:border-0">
                        <div>
                          <p className="font-medium text-gray-900">{item.module_title}</p>
                          <p className="text-sm text-gray-600">{item.course_title}</p>
                        </div>
                        <div className="text-right">
                          {item.completed ? (
                            <span className="badge badge-success">Completed</span>
                          ) : (
                            <span className="badge badge-warning">In Progress</span>
                          )}
                          {item.quiz_score > 0 && (
                            <p className="text-sm text-gray-600 mt-1">Score: {item.quiz_score}%</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
