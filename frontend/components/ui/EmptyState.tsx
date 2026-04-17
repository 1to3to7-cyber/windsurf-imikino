import React from 'react'
import { FileText, Users, Search, Wifi } from 'lucide-react'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  size?: 'sm' | 'md' | 'lg'
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'py-8',
    md: 'py-12',
    lg: 'py-16'
  }
  
  const iconSizes = {
    sm: 'w-12 h-12',
    md: 'w-16 h-16',
    lg: 'w-20 h-20'
  }
  
  return (
    <div className={sizeClasses[size]}>
      <div className="text-center">
        {icon && (
          <div className="flex justify-center mb-4">
            <div className={iconSizes[size]}>
              {icon}
            </div>
          </div>
        )}
        
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          {title}
        </h3>
        
        {description && (
          <p className="text-gray-500 mb-6 max-w-md mx-auto">
            {description}
          </p>
        )}
        
        {action && (
          <button
            onClick={action.onClick}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            {action.label}
          </button>
        )}
      </div>
    </div>
  )
}

// Predefined empty states for common scenarios
export const EmptyPosts = ({ onRefresh }: { onRefresh?: () => void }) => (
  <EmptyState
    icon={<FileText className="text-gray-400" />}
    title="No posts yet"
    description="Be the first to share something with the community!"
    action={onRefresh ? {
      label: "Refresh",
      onClick: onRefresh
    } : undefined}
  />
)

export const EmptyCourses = ({ onExplore }: { onExplore?: () => void }) => (
  <EmptyState
    icon={<FileText className="text-gray-400" />}
    title="No courses available"
    description="Courses are being prepared. Check back soon!"
    action={onExplore ? {
      label: "Explore Other Content",
      onClick: onExplore
    } : undefined}
  />
)

export const EmptyTasks = ({ onBrowse }: { onBrowse?: () => void }) => (
  <EmptyState
    icon={<Users className="text-gray-400" />}
    title="No tasks available"
    description="New tasks will be posted soon. Check back later!"
    action={onBrowse ? {
      label: "Browse Marketplace",
      onClick: onBrowse
    } : undefined}
  />
)

export const EmptySearch = ({ onClear }: { onClear?: () => void }) => (
  <EmptyState
    icon={<Search className="text-gray-400" />}
    title="No results found"
    description="Try adjusting your search terms or filters."
    action={onClear ? {
      label: "Clear Filters",
      onClick: onClear
    } : undefined}
  />
)

export const EmptyNetwork = ({ onRetry }: { onRetry?: () => void }) => (
  <EmptyState
    icon={<Wifi className="text-gray-400" />}
    title="Connection lost"
    description="Please check your internet connection and try again."
    action={onRetry ? {
      label: "Retry",
      onClick: onRetry
    } : undefined}
  />
)

export const EmptyProfile = ({ onEdit }: { onEdit?: () => void }) => (
  <EmptyState
    icon={<Users className="text-gray-400" />}
    title="Profile not complete"
    description="Complete your profile to connect with others."
    action={onEdit ? {
      label: "Edit Profile",
      onClick: onEdit
    } : undefined}
  />
)
