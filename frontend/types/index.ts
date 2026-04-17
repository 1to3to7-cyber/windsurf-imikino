// User types
export interface User {
  id: number;
  email: string;
  display_name: string;
  xp: number;
  role: 'user' | 'admin';
  badges: string[];
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Post types
export interface Post {
  id: number;
  user_id: number;
  content: string;
  media_url?: string;
  type: 'text' | 'image' | 'video';
  likes_count: number;
  created_at: string;
  user: User;
}

export interface Comment {
  id: number;
  post_id: number;
  user_id: number;
  content: string;
  created_at: string;
  user: User;
}

// Course types
export interface Module {
  id: string;
  title: string;
  type: 'text' | 'video';
  content: string;
  completed?: boolean;
  quiz_score?: number;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  thumbnail_url?: string;
  modules: Module[];
  created_at: string;
  progress?: {
    completed_modules: number;
    total_modules: number;
    completion_percentage: number;
  };
}

export interface Question {
  question: string;
  options: string[];
  type: 'multiple_choice';
}

export interface Quiz {
  id: number;
  module_id: string;
  questions: Question[];
}

export interface QuizSubmission {
  answers: number[];
}

export interface QuizResult {
  score: number;
  total_questions: number;
  score_percentage: number;
  passed: boolean;
  xp_awarded: number;
}

// Task types
export interface Task {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  deadline?: string;
  proof_type: 'text' | 'image' | 'link';
  status: 'open' | 'closed';
  created_at: string;
  user_submission?: {
    id: number;
    status: 'pending' | 'approved' | 'rejected';
    submitted_at: string;
    proof_content?: string;
  };
}

export interface TaskSubmission {
  proof_content: string;
}

export interface Submission {
  id: number;
  task_id: number;
  user_id: number;
  proof_content: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  task: Task;
  user: User;
}

// Progress types
export interface UserProgress {
  user: User;
  progress: Array<{
    user_id: number;
    course_id: number;
    module_id: string;
    completed: boolean;
    quiz_score: number;
    course_title: string;
    module_title: string;
  }>;
  total_courses_completed: number;
}

// Admin types
export interface ModerationAction {
  action: 'approve' | 'reject';
  reason?: string;
}

export interface AdminStats {
  total_users: number;
  pending_submissions: number;
  total_posts: number;
  total_tasks: number;
  completed_tasks: number;
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

// Form types
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  display_name: string;
}

export interface PostFormData {
  content: string;
  media_url?: string;
  type: 'text' | 'image' | 'video';
}

export interface CommentFormData {
  content: string;
}

// UI State types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface PaginationState {
  page: number;
  limit: number;
  total?: number;
  hasMore: boolean;
}

// Context types
export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<AuthResponse>;
  register: (email: string, password: string, display_name: string) => Promise<AuthResponse>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}

export interface UIContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  showToast: (message: string, type?: 'success' | 'error' | 'info') => void;
  isOnline: boolean;
}

// Badge types
export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

export const BADGES: Badge[] = [
  {
    id: 'founder',
    name: 'Founder',
    description: 'Early member of Imikino',
    icon: '🌟',
    color: 'primary'
  },
  {
    id: 'admin',
    name: 'Admin',
    description: 'Platform administrator',
    icon: '👑',
    color: 'error'
  },
  {
    id: 'course_complete',
    name: 'Course Complete',
    description: 'Completed first course',
    icon: '🎓',
    color: 'success'
  },
  {
    id: 'task_starter',
    name: 'Task Starter',
    description: 'Completed first task',
    icon: '🚀',
    color: 'primary'
  },
  {
    id: 'task_achiever',
    name: 'Task Achiever',
    description: 'Completed 5 tasks',
    icon: '⭐',
    color: 'warning'
  },
  {
    id: 'task_master',
    name: 'Task Master',
    description: 'Completed 10 tasks',
    icon: '🏆',
    color: 'success'
  }
];
