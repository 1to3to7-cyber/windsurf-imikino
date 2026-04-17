'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Course } from '@/types';
import Link from 'next/link';

export default function CoursesPage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadCourses();
    }
  }, [user]);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const coursesData = await apiClient.getCourses();
      setCourses(coursesData);
    } catch (err: any) {
      setError(err.message || 'Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to view courses</p>
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
          <p className="text-gray-600">Loading courses...</p>
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
            <h1 className="text-xl font-bold text-gray-900">Courses</h1>
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

        {/* Courses Grid */}
        {courses.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No courses available yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CourseCard({ course }: { course: Course }) {
  const progress = course.progress;
  const completionPercentage = progress?.completion_percentage || 0;

  return (
    <Link href={`/courses/${course.id}`} className="block">
      <div className="card hover:shadow-md transition-shadow duration-200">
        {course.thumbnail_url && (
          <div className="aspect-video bg-gray-200 rounded-t-lg overflow-hidden">
            <img
              src={course.thumbnail_url}
              alt={course.title}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          </div>
        )}
        <div className="card-body">
          <h3 className="font-bold text-lg text-gray-900 mb-2">{course.title}</h3>
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {course.description}
          </p>
          
          {/* Progress Bar */}
          {progress && (
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Progress</span>
                <span>{Math.round(completionPercentage)}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${completionPercentage}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {progress.completed_modules} of {progress.total_modules} modules completed
              </p>
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">
              {course.modules.length} modules
            </span>
            <span className="text-primary-600 font-medium text-sm">
              {progress ? 'Continue' : 'Start'} →
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
