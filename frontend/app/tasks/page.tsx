'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Task } from '@/types';
import Link from 'next/link';

export default function TasksPage() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadTasks();
    }
  }, [user]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const tasksData = await apiClient.getTasks();
      setTasks(tasksData);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to view tasks</p>
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
          <p className="text-gray-600">Loading tasks...</p>
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
            <h1 className="text-xl font-bold text-gray-900">Tasks</h1>
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

        {/* Tasks Grid */}
        {tasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No tasks available yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tasks.map((task) => (
              <TaskCard key={task.id} task={task} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TaskCard({ task }: { task: Task }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'success';
      case 'closed':
        return 'error';
      default:
        return 'gray';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'open':
        return 'Available';
      case 'closed':
        return 'Closed';
      default:
        return status;
    }
  };

  const getSubmissionStatus = () => {
    if (!task.user_submission) return null;
    
    switch (task.user_submission.status) {
      case 'pending':
        return { text: 'Pending Review', color: 'warning' };
      case 'approved':
        return { text: 'Completed', color: 'success' };
      case 'rejected':
        return { text: 'Needs Revision', color: 'error' };
      default:
        return { text: task.user_submission.status, color: 'gray' };
    }
  };

  const submissionStatus = getSubmissionStatus();

  return (
    <Link href={`/tasks/${task.id}`} className="block">
      <div className="card hover:shadow-md transition-shadow duration-200">
        <div className="card-body">
          {/* Status Badge */}
          <div className="flex items-center justify-between mb-3">
            <span className={`badge badge-${getStatusColor(task.status)}`}>
              {getStatusText(task.status)}
            </span>
            <div className="flex items-center text-primary-600 font-bold">
              <span className="text-lg mr-1">⭐</span>
              <span>{task.xp_reward}</span>
            </div>
          </div>

          {/* Task Info */}
          <h3 className="font-bold text-lg text-gray-900 mb-2">{task.title}</h3>
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">
            {task.description}
          </p>

          {/* Proof Type */}
          <div className="flex items-center text-sm text-gray-500 mb-4">
            <span className="font-medium">Proof Type:</span>
            <span className="ml-2 capitalize">{task.proof_type}</span>
          </div>

          {/* Submission Status */}
          {submissionStatus && (
            <div className={`bg-${submissionStatus.color}-50 border border-${submissionStatus.color}-200 rounded-lg p-3`}>
              <div className="flex items-center">
                <span className={`text-${submissionStatus.color}-700 font-medium`}>
                  {submissionStatus.text}
                </span>
                {task.user_submission.submitted_at && (
                  <span className="text-xs text-gray-500 ml-auto">
                    Submitted {new Date(task.user_submission.submitted_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Deadline */}
          {task.deadline && (
            <div className="flex items-center text-sm text-gray-500">
              <span className="font-medium">Deadline:</span>
              <span className="ml-2">
                {new Date(task.deadline).toLocaleDateString()}
              </span>
            </div>
          )}

          {/* Action Button */}
          <div className="mt-4">
            <span className="text-primary-600 font-medium text-sm">
              {task.user_submission ? 'View Details' : 'Start Task'} →
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
