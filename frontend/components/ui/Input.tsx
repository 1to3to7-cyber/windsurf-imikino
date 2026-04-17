import React from 'react'
import { clsx } from 'clsx'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  variant?: 'default' | 'error' | 'success'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  variant = 'default',
  size = 'md',
  fullWidth = false,
  leftIcon,
  rightIcon,
  className,
  ...props
}) => {
  const baseClasses = 'relative block w-full transition-all duration-200'
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-2.5 text-lg'
  }
  
  const variantClasses = {
    default: 'border-2 border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500',
    error: 'border-2 border-error-500 focus:border-error-600 focus:ring-2 focus:ring-error-500',
    success: 'border-2 border-success-500 focus:border-success-600 focus:ring-2 focus:ring-success-500'
  }
  
  const labelClasses = 'block text-sm font-medium text-gray-700 mb-1'
  const inputClasses = clsx(
    baseClasses,
    sizeClasses[size],
    variantClasses[variant],
    leftIcon ? 'pl-10' : '',
    rightIcon ? 'pr-10' : '',
    className
  )
  
  const iconClasses = 'absolute top-1/2 transform -translate-y-1/2 text-gray-400'
  const leftIconClasses = clsx(iconClasses, 'left-3')
  const rightIconClasses = clsx(iconClasses, 'right-3')
  
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label className={labelClasses}>
          {label}
        </label>
      )}
      <div className="relative">
        {leftIcon && (
          <div className={leftIconClasses}>
            {leftIcon}
          </div>
        )}
        <input
          className={inputClasses}
          {...props}
        />
        {rightIcon && (
          <div className={rightIconClasses}>
            {rightIcon}
          </div>
        )}
      </div>
      {error && (
        <p className="mt-1 text-sm text-error-600">
          {error}
        </p>
      )}
      {helperText && !error && (
        <p className="mt-1 text-sm text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  )
}
