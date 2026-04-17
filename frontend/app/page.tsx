'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Post, Comment } from '@/types';
import Link from 'next/link';

export default function HomePage() {
  const { user, isLoading } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newPostContent, setNewPostContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (user) {
      loadPosts();
    }
  }, [user]);

  const loadPosts = async () => {
    try {
      setLoading(true);
      const postsData = await apiClient.getPosts();
      setPosts(postsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPostContent.trim()) return;

    try {
      setSubmitting(true);
      const newPost = await apiClient.createPost(newPostContent);
      setPosts([newPost, ...posts]);
      setNewPostContent('');
    } catch (err: any) {
      setError(err.message || 'Failed to create post');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLike = async (postId: number) => {
    try {
      await apiClient.likePost(postId);
      setPosts(posts.map(post => 
        post.id === postId 
          ? { ...post, likes_count: post.likes_count + 1 }
          : post
      ));
    } catch (err: any) {
      setError(err.message || 'Failed to like post');
    }
  };

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container-mobile py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome to Imikino</h1>
            <p className="text-gray-600 mb-8">Learn, Share, and Grow with Rwandan Youth</p>
            <div className="space-y-4">
              <Link href="/login" className="btn btn-primary w-full max-w-xs mx-auto block">
                Sign In
              </Link>
              <Link href="/signup" className="btn btn-secondary w-full max-w-xs mx-auto block">
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="container-mobile py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-gray-900">Imikino</h1>
            <div className="flex items-center space-x-4">
              <Link href="/courses" className="text-primary-600 hover:text-primary-700">
                Courses
              </Link>
              <Link href="/tasks" className="text-primary-600 hover:text-primary-700">
                Tasks
              </Link>
              <Link href="/profile" className="text-primary-600 hover:text-primary-700">
                Profile
              </Link>
              {user.role === 'admin' && (
                <Link href="/admin" className="text-primary-600 hover:text-primary-700">
                  Admin
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="container-mobile py-6">
        {/* Create Post */}
        <div className="card mb-6">
          <div className="card-body">
            <form onSubmit={handleCreatePost} className="space-y-4">
              <textarea
                value={newPostContent}
                onChange={(e) => setNewPostContent(e.target.value)}
                placeholder="Share what you're learning..."
                className="form-input resize-none"
                rows={3}
                disabled={submitting}
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting || !newPostContent.trim()}
                >
                  {submitting ? 'Posting...' : 'Post'}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-error-50 border border-error-200 text-error-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Posts Feed */}
        <div className="space-y-6">
          {posts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No posts yet. Be the first to share!</p>
            </div>
          ) : (
            posts.map((post) => (
              <PostCard 
                key={post.id} 
                post={post} 
                onLike={handleLike}
                currentUser={user}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function PostCard({ post, onLike, currentUser }: { 
  post: Post; 
  onLike: (postId: number) => void;
  currentUser: any;
}) {
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const [loadingComments, setLoadingComments] = useState(false);

  const loadComments = async () => {
    if (showComments) return;
    
    try {
      setLoadingComments(true);
      const commentsData = await apiClient.getPostComments(post.id);
      setComments(commentsData);
      setShowComments(true);
    } catch (err: any) {
      console.error('Failed to load comments:', err);
    } finally {
      setLoadingComments(false);
    }
  };

  const handleComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setSubmittingComment(true);
      const comment = await apiClient.commentOnPost(post.id, newComment);
      setComments([...comments, comment]);
      setNewComment('');
    } catch (err: any) {
      console.error('Failed to comment:', err);
    } finally {
      setSubmittingComment(false);
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        {/* Post Header */}
        <div className="flex items-center mb-4">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center mr-3">
            <span className="text-primary-600 font-medium">
              {post.user.display_name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="font-medium text-gray-900">{post.user.display_name}</h3>
            <p className="text-sm text-gray-500">
              {new Date(post.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Post Content */}
        <div className="mb-4">
          <p className="text-gray-900 whitespace-pre-wrap">{post.content}</p>
          {post.media_url && (
            <div className="mt-3">
              {post.type === 'image' ? (
                <img 
                  src={post.media_url} 
                  alt="Post image" 
                  className="rounded-lg max-w-full h-auto"
                  loading="lazy"
                />
              ) : post.type === 'video' ? (
                <div className="aspect-video bg-gray-200 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Video: {post.media_url}</p>
                </div>
              ) : null}
            </div>
          )}
        </div>

        {/* Post Actions */}
        <div className="flex items-center space-x-4 text-sm">
          <button
            onClick={() => onLike(post.id)}
            className="flex items-center space-x-1 text-gray-500 hover:text-primary-600 transition-colors"
          >
            <span>❤️</span>
            <span>{post.likes_count}</span>
          </button>
          <button
            onClick={loadComments}
            className="flex items-center space-x-1 text-gray-500 hover:text-primary-600 transition-colors"
          >
            <span>💬</span>
            <span>Comment</span>
          </button>
        </div>

        {/* Comments Section */}
        {showComments && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            {/* Add Comment */}
            <form onSubmit={handleComment} className="mb-4">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment..."
                  className="form-input flex-1"
                  disabled={submittingComment}
                />
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submittingComment || !newComment.trim()}
                >
                  {submittingComment ? '...' : 'Send'}
                </button>
              </div>
            </form>

            {/* Comments List */}
            {loadingComments ? (
              <div className="text-center py-4">
                <div className="loading-spinner w-6 h-6 mx-auto"></div>
              </div>
            ) : (
              <div className="space-y-3">
                {comments.map((comment) => (
                  <div key={comment.id} className="flex space-x-3">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-gray-600 text-sm font-medium">
                        {comment.user.display_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="bg-gray-50 rounded-lg px-3 py-2">
                        <p className="font-medium text-sm text-gray-900">
                          {comment.user.display_name}
                        </p>
                        <p className="text-gray-700">{comment.content}</p>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(comment.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
