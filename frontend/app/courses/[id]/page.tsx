'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Course, Quiz, QuizResult } from '@/types';
import { useParams, useRouter } from 'next/navigation';

export default function CoursePage() {
  const { user } = useAuth();
  const params = useParams();
  const router = useRouter();
  const courseId = parseInt(params.id as string);
  
  const [course, setCourse] = useState<Course | null>(null);
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<number[]>([]);
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user && courseId) {
      loadCourse();
    }
  }, [user, courseId]);

  const loadCourse = async () => {
    try {
      setLoading(true);
      const courseData = await apiClient.getCourse(courseId);
      setCourse(courseData);
    } catch (err: any) {
      setError(err.message || 'Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  const loadQuiz = async (moduleId: string) => {
    try {
      const quizData = await apiClient.getModuleQuiz(courseId, moduleId);
      setQuiz(quizData);
      setQuizAnswers(new Array(quizData.questions.length).fill(-1));
      setShowQuiz(true);
    } catch (err: any) {
      setError(err.message || 'Failed to load quiz');
    }
  };

  const completeModule = async (moduleId: string) => {
    try {
      setSubmitting(true);
      await apiClient.completeModule(courseId, moduleId);
      // Reload course to update progress
      await loadCourse();
    } catch (err: any) {
      setError(err.message || 'Failed to complete module');
    } finally {
      setSubmitting(false);
    }
  };

  const submitQuiz = async () => {
    if (!quiz) return;
    
    try {
      setSubmitting(true);
      const result = await apiClient.submitQuiz(courseId, quiz.module_id, quizAnswers);
      setQuizResult(result);
      // Reload course to update progress
      await loadCourse();
    } catch (err: any) {
      setError(err.message || 'Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to view this course</p>
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
          <p className="text-gray-600">Loading course...</p>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Course not found</p>
          <button onClick={() => router.push('/courses')} className="btn btn-primary">
            Back to Courses
          </button>
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
              onClick={() => router.push('/courses')} 
              className="text-xl font-bold text-gray-900"
            >
              ← Back to Courses
            </button>
            <h1 className="text-xl font-bold text-gray-900 truncate">{course.title}</h1>
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

        {/* Course Info */}
        <div className="card mb-6">
          <div className="card-body">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{course.title}</h2>
            <p className="text-gray-600 mb-4">{course.description}</p>
            <div className="flex items-center text-sm text-gray-500">
              <span>{course.modules.length} modules</span>
              <span className="mx-2">•</span>
              <span>Self-paced learning</span>
            </div>
          </div>
        </div>

        {/* Modules */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-gray-900">Course Modules</h3>
          {course.modules.map((module, index) => (
            <div key={module.id} className="card">
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <h4 className="font-medium text-gray-900">Module {index + 1}: {module.title}</h4>
                      {module.completed && (
                        <span className="badge badge-success ml-2">Completed</span>
                      )}
                      {module.quiz_score > 0 && (
                        <span className="badge badge-primary ml-2">Score: {module.quiz_score}%</span>
                      )}
                    </div>
                    
                    {!showQuiz || selectedModule !== module.id ? (
                      <div className="text-gray-700 mb-4">
                        <p>{module.content}</p>
                      </div>
                    ) : null}
                  </div>

                  <div className="flex flex-col space-y-2 ml-4">
                    {!showQuiz || selectedModule !== module.id ? (
                      <>
                        {!module.completed && (
                          <button
                            onClick={() => completeModule(module.id)}
                            className="btn btn-success"
                            disabled={submitting}
                          >
                            {submitting ? '...' : 'Mark Complete'}
                          </button>
                        )}
                        <button
                          onClick={() => loadQuiz(module.id)}
                          className="btn btn-primary"
                          disabled={submitting}
                        >
                          Take Quiz
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => {
                          setShowQuiz(false);
                          setSelectedModule(null);
                          setQuiz(null);
                          setQuizResult(null);
                        }}
                        className="btn btn-secondary"
                      >
                        Back to Content
                      </button>
                    )}
                  </div>
                </div>

                {/* Quiz Section */}
                {showQuiz && selectedModule === module.id && quiz && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h5 className="font-medium text-gray-900 mb-4">Module Quiz</h5>
                    
                    {!quizResult ? (
                      <div className="space-y-4">
                        {quiz.questions.map((question, qIndex) => (
                          <div key={qIndex} className="bg-gray-50 p-4 rounded-lg">
                            <p className="font-medium text-gray-900 mb-3">{question.question}</p>
                            <div className="space-y-2">
                              {question.options.map((option, oIndex) => (
                                <label key={oIndex} className="flex items-center space-x-2 cursor-pointer">
                                  <input
                                    type="radio"
                                    name={`question-${qIndex}`}
                                    value={oIndex}
                                    checked={quizAnswers[qIndex] === oIndex}
                                    onChange={() => {
                                      const newAnswers = [...quizAnswers];
                                      newAnswers[qIndex] = oIndex;
                                      setQuizAnswers(newAnswers);
                                    }}
                                    className="w-4 h-4 text-primary-600"
                                  />
                                  <span className="text-gray-700">{option}</span>
                                </label>
                              ))}
                            </div>
                          </div>
                        ))}
                        
                        <button
                          onClick={submitQuiz}
                          className="btn btn-primary w-full"
                          disabled={submitting || quizAnswers.includes(-1)}
                        >
                          {submitting ? 'Submitting...' : 'Submit Quiz'}
                        </button>
                      </div>
                    ) : (
                      <div className="text-center">
                        <div className={`text-6xl mb-4 ${quizResult.passed ? 'text-success-600' : 'text-error-600'}`}>
                          {quizResult.passed ? '✓' : '✗'}
                        </div>
                        <h5 className={`text-xl font-bold mb-2 ${quizResult.passed ? 'text-success-900' : 'text-error-900'}`}>
                          {quizResult.passed ? 'Quiz Passed!' : 'Quiz Failed'}
                        </h5>
                        <p className="text-gray-600 mb-4">
                          Your score: {quizResult.score}/{quizResult.total_questions} ({quizResult.score_percentage}%)
                        </p>
                        {quizResult.xp_awarded > 0 && (
                          <p className="text-success-700 font-medium">
                            +{quizResult.xp_awarded} XP earned!
                          </p>
                        )}
                        <button
                          onClick={() => {
                            setShowQuiz(false);
                            setSelectedModule(null);
                            setQuiz(null);
                            setQuizResult(null);
                          }}
                          className="btn btn-primary"
                        >
                          Continue
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
