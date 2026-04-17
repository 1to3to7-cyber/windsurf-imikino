import React from 'react'
import { clsx } from 'clsx'

interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  color?: 'primary' | 'secondary' | 'white' | 'gray'
  className?: string
  text?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className,
  text
}) => {
  const sizeClasses = {
    xs: 'w-4 h-4',
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  }
  
  const colorClasses = {
    primary: 'text-primary-600',
    secondary: 'text-secondary-600',
    white: 'text-white',
    gray: 'text-gray-500'
  }
  
  return (
    <div className={clsx('flex flex-col items-center justify-center', className)}>
      <div className={clsx(
        'animate-spin rounded-full border-2 border-t-transparent',
        sizeClasses[size],
        colorClasses[color],
        'border-current'
      )} />
      {text && (
        <p className={clsx(
          'mt-2 text-sm font-medium',
          colorClasses[color]
        )}>
          {text}
        </p>
      )}
    </div>
  )
}

// Loading skeleton component for content placeholders
interface LoadingSkeletonProps {
  lines?: number
  className?: string
  height?: string
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  lines = 3,
  className,
  height = 'h-4'
}) => {
  return (
    <div className={clsx('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={clsx(
            'bg-gray-200 rounded animate-pulse',
            height
          )}
        />
      ))}
    </div>
  )
}

// Full page loading component
export const FullPageLoading: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <LoadingSpinner size="lg" text={text} />
    </div>
  )
}
