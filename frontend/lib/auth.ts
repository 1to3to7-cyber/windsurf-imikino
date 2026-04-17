'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { AuthContextType, User, AuthResponse } from '@/types';
import { apiClient, ApiError } from '@/lib/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = () => {
      try {
        const storedToken = localStorage.getItem('imikino_token');
        const storedUser = localStorage.getItem('imikino_user');
        
        if (storedToken && storedUser) {
          setToken(storedToken);
          apiClient.setToken(storedToken);
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        // Clear corrupted data
        localStorage.removeItem('imikino_token');
        localStorage.removeItem('imikino_user');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<AuthResponse> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.login(email, password);
      
      // Store in localStorage
      localStorage.setItem('imikino_token', response.access_token);
      localStorage.setItem('imikino_user', JSON.stringify(response.user));
      
      // Update state
      setToken(response.access_token);
      setUser(response.user);
      apiClient.setToken(response.access_token);
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, display_name: string): Promise<AuthResponse> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.register(email, password, display_name);
      
      // Store in localStorage
      localStorage.setItem('imikino_token', response.access_token);
      localStorage.setItem('imikino_user', JSON.stringify(response.user));
      
      // Update state
      setToken(response.access_token);
      setUser(response.user);
      apiClient.setToken(response.access_token);
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Registration failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('imikino_token');
    localStorage.removeItem('imikino_user');
    
    // Clear state
    setToken(null);
    setUser(null);
    apiClient.setToken(null);
    setError(null);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    isLoading,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Hook to protect routes
export function useRequireAuth() {
  const auth = useAuth();
  
  useEffect(() => {
    if (!auth.isLoading && !auth.user) {
      // Redirect to login page
      window.location.href = '/login';
    }
  }, [auth.user, auth.isLoading]);
  
  return auth;
}
