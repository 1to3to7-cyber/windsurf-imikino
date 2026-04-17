import { ApiResponse, AuthResponse, User, Post, Comment, Course, Quiz, QuizSubmission, QuizResult, Task, TaskSubmission, Submission, UserProgress, ModerationAction, AdminStats } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        // Add timeout for mobile networks
        signal: AbortSignal.timeout(30000),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new ApiError(
          data.message || data.detail || 'Request failed',
          response.status,
          data
        );
      }

      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new ApiError('Request timeout. Please check your connection.', 408);
      }
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new ApiError('Network error. Please check your internet connection.', 0);
      }
      
      throw new ApiError('An unexpected error occurred', 500);
    }
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string, display_name: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, display_name }),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/users/me');
  }

  async getUserProgress(): Promise<UserProgress> {
    return this.request<UserProgress>('/users/me/progress');
  }

  // Posts endpoints
  async getPosts(): Promise<Post[]> {
    return this.request<Post[]>('/posts');
  }

  async createPost(content: string, media_url?: string, type: 'text' | 'image' | 'video' = 'text'): Promise<Post> {
    return this.request<Post>('/posts', {
      method: 'POST',
      body: JSON.stringify({ content, media_url, type }),
    });
  }

  async likePost(postId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/posts/${postId}/like`, {
      method: 'POST',
    });
  }

  async commentOnPost(postId: number, content: string): Promise<Comment> {
    return this.request<Comment>(`/posts/${postId}/comment`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  async getPostComments(postId: number): Promise<Comment[]> {
    return this.request<Comment[]>(`/posts/${postId}/comments`);
  }

  // Courses endpoints
  async getCourses(): Promise<Course[]> {
    return this.request<Course[]>('/courses');
  }

  async getCourse(courseId: number): Promise<Course> {
    return this.request<Course>(`/courses/${courseId}`);
  }

  async getModuleQuiz(courseId: number, moduleId: string): Promise<Quiz> {
    return this.request<Quiz>(`/courses/${courseId}/quizzes/${moduleId}`);
  }

  async submitQuiz(courseId: number, moduleId: string, answers: number[]): Promise<QuizResult> {
    return this.request<QuizResult>(`/courses/${courseId}/quizzes/${moduleId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });
  }

  async completeModule(courseId: number, moduleId: string): Promise<{ message: string; xp_awarded: number }> {
    return this.request<{ message: string; xp_awarded: number }>(`/courses/${courseId}/modules/${moduleId}/complete`, {
      method: 'POST',
    });
  }

  // Tasks endpoints
  async getTasks(): Promise<Task[]> {
    return this.request<Task[]>('/tasks');
  }

  async getTask(taskId: number): Promise<Task> {
    return this.request<Task>(`/tasks/${taskId}`);
  }

  async claimTask(taskId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/tasks/${taskId}/claim`, {
      method: 'POST',
    });
  }

  async submitTask(taskId: number, proof_content: string): Promise<{ message: string; submission_id: number; xp_awarded: number }> {
    return this.request<{ message: string; submission_id: number; xp_awarded: number }>(`/tasks/${taskId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ proof_content }),
    });
  }

  async getTaskSubmissions(taskId: number): Promise<Submission[]> {
    return this.request<Submission[]>(`/tasks/${taskId}/submissions`);
  }

  // Admin endpoints
  async getPendingSubmissions(): Promise<Submission[]> {
    return this.request<Submission[]>('/admin/submissions');
  }

  async moderateSubmission(submissionId: number, action: ModerationAction): Promise<{ message: string; submission_id: number; xp_awarded: number; action: string }> {
    return this.request<{ message: string; submission_id: number; xp_awarded: number; action: string }>(`/admin/submissions/${submissionId}/moderate`, {
      method: 'POST',
      body: JSON.stringify(action),
    });
  }

  async getAdminPosts(): Promise<Post[]> {
    return this.request<Post[]>('/admin/posts');
  }

  async moderatePost(postId: number, action: ModerationAction): Promise<{ message: string; post_id: number; action: string; reason?: string }> {
    return this.request<{ message: string; post_id: number; action: string; reason?: string }>(`/admin/posts/${postId}/moderate`, {
      method: 'POST',
      body: JSON.stringify(action),
    });
  }

  async getAllUsers(): Promise<User[]> {
    return this.request<User[]>('/admin/users');
  }

  async toggleUserRole(userId: number): Promise<{ message: string; user_id: number; new_role: string }> {
    return this.request<{ message: string; user_id: number; new_role: string }>(`/admin/users/${userId}/toggle-role`, {
      method: 'POST',
    });
  }

  async getAdminDashboard(): Promise<{ stats: AdminStats; admin: User }> {
    return this.request<{ stats: AdminStats; admin: User }>('/admin/dashboard');
  }
}

export const apiClient = new ApiClient();
export { ApiError };
