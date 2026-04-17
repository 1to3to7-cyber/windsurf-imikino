'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Task } from '@/types';
import { useParams, useRouter } from 'next/navigation';

export default function TaskDetailPage() {
  const { user } = useAuth();
  const params = useParams();
  const router = useRouter();
  const taskId = parseInt(params.id as string);
  
  const [task, setTask] = useState<Task | null>(null);
  const [proofContent, setProofContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user && taskId) {
      loadTask();
    }
  }, [user, taskId]);

  const loadTask = async () => {
    try {
      setLoading(true);
      const taskData = await apiClient.getTask(taskId);
      setTask(taskData);
    } catch (err: any) {
      setError(err.message || 'Failed to load task');
    } finally {
      setLoading(false);
    }
  };

  const claimTask = async () => {
    try {
      setSubmitting(true);
      await apiClient.claimTask(taskId);
      // Reload task to update status
      await loadTask();
    } catch (err: any) {
      setError(err.message || 'Failed to claim task');
    } finally {
      setSubmitting(false);
    }
  };

  const submitTask = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!proofContent.trim()) {
      setError('Please provide proof content');
      return;
    }

    try {
      setSubmitting(true);
      await apiClient.submitTask(taskId, proofContent);
      // Reload task to update status
      await loadTask();
      setProofContent('');
    } catch (err: any) {
      setError(err.message || 'Failed to submit task');
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to view this task</p>
          <button onClick={() => router.push('/login')} className="btn btn-primary">
            Sign In
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
          <p className="text-gray-600">Loading task...</p>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Task not found</p>
          <button onClick={() => router.push('/tasks')} className="btn btn-primary">
            Back to Tasks
          </button>
        </div>
      </div>
    );
  }

  const hasSubmitted = task.user_submission !== undefined;
  const isClaimed = hasSubmitted;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container-mobile py-4">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => router.push('/tasks')} 
              className="text-xl font-bold text-gray-900"
            >
              ← Back to Tasks
            </button>
            <h1 className="text-xl font-bold text-gray-900 truncate">Task Details</h1>
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

        {/* Task Info */}
        <div className="card mb-6">
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900">{task.title}</h2>
              <div className="flex items-center text-primary-600 font-bold">
                <span className="text-lg mr-1">⭐</span>
                <span className="text-lg">{task.xp_reward}</span>
              </div>
            </div>

            <div className="text-gray-700 mb-6">
              <p className="whitespace-pre-wrap">{task.description}</p>
            </div>

            {/* Task Metadata */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm text-gray-500 mb-1">Proof Type</p>
                <p className="font-medium text-gray-900 capitalize">{task.proof_type}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm text-gray-500 mb-1">Status</p>
                <p className="font-medium text-gray-900 capitalize">{task.status}</p>
              </div>
            </div>

            {/* Deadline */}
            {task.deadline && (
              <div className="bg-warning-50 border border-warning-200 rounded-lg p-3">
                <p className="text-sm text-warning-700 mb-1">Deadline</p>
                <p className="font-medium text-warning-900">
                  {new Date(task.deadline).toLocaleDateString()}
                </p>
              </div>
            )}

            {/* Submission Status */}
            {hasSubmitted && (
              <div className={`rounded-lg p-3 ${
                task.user_submission?.status === 'approved' ? 'bg-success-50 border border-success-200' :
                task.user_submission?.status === 'rejected' ? 'bg-error-50 border border-error-200' :
                'bg-warning-50 border border-warning-200'
              }`}>
                <p className={`text-sm mb-1 ${
                  task.user_submission?.status === 'approved' ? 'text-success-700' :
                  task.user_submission?.status === 'rejected' ? 'text-error-700' :
                  'text-warning-700'
                }`}>
                  Your Submission Status
                </p>
                <p className={`font-medium capitalize ${
                  task.user_submission?.status === 'approved' ? 'text-success-900' :
                  task.user_submission?.status === 'rejected' ? 'text-error-900' :
                  'text-warning-900'
                }`}>
                  {task.user_submission?.status}
                </p>
                {task.user_submission?.submitted_at && (
                  <p className="text-xs text-gray-500 mt-2">
                    Submitted {new Date(task.user_submission.submitted_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Task Actions */}
        {!hasSubmitted && (
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Complete This Task</h3>
              
              {!isClaimed ? (
                <div className="text-center">
                  <button
                    onClick={claimTask}
                    className="btn btn-primary"
                    disabled={submitting}
                  >
                    {submitting ? '...' : 'Claim Task'}
                  </button>
                  <p className="text-sm text-gray-600 mt-2">
                    Claim this task to start working on it
                  </p>
                </div>
              ) : (
                <form onSubmit={submitTask} className="space-y-4">
                  <div>
                    <label htmlFor="proof" className="form-label">
                      {task.proof_type === 'image' ? 'Image URL' :
                       task.proof_type === 'link' ? 'Link URL' :
                       'Proof Content'}
                    </label>
                    <textarea
                      id="proof"
                      value={proofContent}
                      onChange={(e) => setProofContent(e.target.value)}
                      placeholder={
                        task.proof_type === 'image' ? 'Enter the URL to your image proof...' :
                        task.proof_type === 'link' ? 'Enter the URL to your work...' :
                        'Describe your completed task and provide any relevant links...'
                      }
                      className="form-input resize-none"
                      rows={4}
                      disabled={submitting}
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn btn-primary w-full"
                    disabled={submitting || !proofContent.trim()}
                  >
                    {submitting ? 'Submitting...' : 'Submit Task'}
                  </button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* Submitted Content Display */}
        {hasSubmitted && task.user_submission?.proof_content && (
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Your Submission</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-wrap">
                  {task.user_submission.proof_content}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
