import React, { useState, useEffect, useRef } from 'react'
import { clsx } from 'clsx'

interface MobileOptimizedProps {
  children: React.ReactNode
  className?: string
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export const MobileOptimized: React.FC<MobileOptimizedProps> = ({
  children,
  className,
  maxWidth = 'full',
  padding = 'md'
}) => {
  const [isMobile, setIsMobile] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const checkMobile = () => {
      if (containerRef.current) {
        const width = containerRef.current.offsetWidth
        setIsMobile(width < 768) // Mobile breakpoint
      }
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    
    return () => {
      window.removeEventListener('resize', checkMobile)
    }
  }, [])

  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md', 
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-full'
  }
  
  const paddingClasses = {
    none: '',
    sm: 'p-2 sm:p-4',
    md: 'p-4 sm:p-6',
    lg: 'p-6 sm:p-8'
  }
  
  return (
    <div 
      ref={containerRef}
      className={clsx(
        'w-full',
        maxWidthClasses[maxWidth],
        paddingClasses[padding],
        isMobile ? 'touch-manipulation' : '',
        className
      )}
      style={{
        WebkitTapHighlightColor: 'transparent',
        WebkitTouchCallout: 'none',
        WebkitUserSelect: isMobile ? 'none' : 'auto',
        overscrollBehavior: 'contain'
      }}
    >
      {children}
    </div>
  )
}

// Mobile-optimized button with touch feedback
interface MobileButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  loading?: boolean
  children: React.ReactNode
}

export const MobileButton: React.FC<MobileButtonProps> = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  children,
  className,
  ...props
}) => {
  const [isPressed, setIsPressed] = useState(false)

  const baseClasses = 'relative overflow-hidden transition-all duration-200 transform active:scale-95'
  
  const variantClasses = {
    primary: 'bg-primary-600 text-white active:bg-primary-700',
    secondary: 'bg-secondary-600 text-white active:bg-secondary-700',
    ghost: 'border-2 border-primary-600 text-primary-600 active:bg-primary-50'
  }
  
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm min-h-[44px]', // iOS touch target
    md: 'px-6 py-3 text-base min-h-[48px]',
    lg: 'px-8 py-4 text-lg min-h-[52px]'
  }
  
  return (
    <button
      className={clsx(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        fullWidth ? 'w-full' : '',
        'focus:outline-none focus:ring-2 focus:ring-primary-500',
        className
      )}
      onTouchStart={() => setIsPressed(true)}
      onTouchEnd={() => setIsPressed(false)}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      disabled={loading}
      {...props}
    >
      <div className={clsx(
        'flex items-center justify-center',
        isPressed ? 'scale-95' : 'scale-100'
      )}>
        {loading ? (
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : (
          children
        )}
      </div>
    </button>
  )
}

// Mobile-optimized input with proper touch handling
interface MobileInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  type?: 'text' | 'email' | 'password' | 'number' | 'tel'
  placeholder?: string
  fullWidth?: boolean
}

export const MobileInput: React.FC<MobileInputProps> = ({
  label,
  error,
  type = 'text',
  placeholder,
  fullWidth = false,
  className,
  ...props
}) => {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const input = inputRef.current
    if (input && 'ontouchstart' in window) {
      // Prevent zoom on focus for mobile
      input.addEventListener('touchstart', (e) => {
        e.preventDefault()
        input.focus()
      })
      
      // Prevent zoom on double tap
      let lastTouchEnd = 0
      input.addEventListener('touchend', () => {
        const now = Date.now()
        if (now - lastTouchEnd < 300) {
          e.preventDefault()
        }
        lastTouchEnd = now
      })
    }
  }, [])

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      <input
        ref={inputRef}
        type={type}
        placeholder={placeholder}
        className={clsx(
          'w-full px-4 py-3 border-2 border-gray-300 rounded-lg',
          'focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          'text-base placeholder-gray-500',
          error ? 'border-error-500' : 'focus:border-primary-500',
          className
        )}
        style={{
          fontSize: '16px', // Prevent zoom on iOS
          WebkitAppearance: 'none',
          WebkitBorderRadius: '0',
          borderRadius: '8px'
        }}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-error-600">
          {error}
        </p>
      )}
    </div>
  )
}

// Swipeable card component for mobile interactions
interface SwipeableCardProps {
  children: React.ReactNode
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  className?: string
}

export const SwipeableCard: React.FC<SwipeableCardProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  className
}) => {
  const cardRef = useRef<HTMLDivElement>(null)
  const [startX, setStartX] = useState(0)
  const [currentX, setCurrentX] = useState(0)
  const [isDragging, setIsDragging] = useState(false)

  useEffect(() => {
    const card = cardRef.current
    if (!card) return

    const handleTouchStart = (e: TouchEvent) => {
      setIsDragging(true)
      setStartX(e.touches[0].clientX)
      setCurrentX(e.touches[0].clientX)
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (!isDragging) return
      
      const touch = e.touches[0]
      setCurrentX(touch.clientX)
      
      // Visual feedback during swipe
      const deltaX = touch.clientX - startX
      const rotation = Math.max(-15, Math.min(15, deltaX * 0.1))
      card.style.transform = `translateX(${deltaX}px) rotate(${rotation}deg)`
    }

    const handleTouchEnd = () => {
      if (!isDragging) return
      
      setIsDragging(false)
      const deltaX = currentX - startX
      
      // Reset transform
      card.style.transform = 'translateX(0) rotate(0)'
      
      // Trigger swipe actions
      if (Math.abs(deltaX) > 50) {
        if (deltaX > 0 && onSwipeRight) {
          onSwipeRight()
        } else if (deltaX < 0 && onSwipeLeft) {
          onSwipeLeft()
        }
      }
    }

    card.addEventListener('touchstart', handleTouchStart, { passive: true })
    card.addEventListener('touchmove', handleTouchMove, { passive: true })
    card.addEventListener('touchend', handleTouchEnd, { passive: true })

    return () => {
      card.removeEventListener('touchstart', handleTouchStart)
      card.removeEventListener('touchmove', handleTouchMove)
      card.removeEventListener('touchend', handleTouchEnd)
    }
  }, [startX, currentX, isDragging, onSwipeLeft, onSwipeRight])

  return (
    <div
      ref={cardRef}
      className={clsx(
        'bg-white rounded-lg shadow-md overflow-hidden',
        'transition-transform duration-200 ease-out',
        'touch-pan-y', // Allow vertical scrolling
        className
      )}
      style={{
        touchAction: 'pan-y pinch-zoom' // Allow vertical pan and zoom
      }}
    >
      {children}
    </div>
  )
}
