import { useCallback } from 'react'

interface ToastOptions {
  duration?: number
  type?: 'success' | 'error' | 'warning' | 'info'
}

export const useToast = () => {
  const showToast = useCallback((message: string, options: ToastOptions = {}) => {
    const { duration = 3000, type = 'info' } = options
    
    // Create toast element
    const toast = document.createElement('div')
    toast.className = `
      fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-white font-medium
      ${type === 'success' ? 'bg-green-500' : ''}
      ${type === 'error' ? 'bg-red-500' : ''}
      ${type === 'warning' ? 'bg-yellow-500' : ''}
      ${type === 'info' ? 'bg-blue-500' : ''}
      transform translate-x-full transition-transform duration-300
    `
    toast.textContent = message
    
    // Add to DOM
    document.body.appendChild(toast)
    
    // Animate in
    setTimeout(() => {
      toast.classList.remove('translate-x-full')
    }, 100)
    
    // Remove after duration
    setTimeout(() => {
      toast.classList.add('translate-x-full')
      setTimeout(() => {
        if (document.body.contains(toast)) {
          document.body.removeChild(toast)
        }
      }, 300)
    }, duration)
  }, [])

  const success = useCallback((message: string, options?: Omit<ToastOptions, 'type'>) => {
    showToast(message, { ...options, type: 'success' })
  }, [showToast])

  const error = useCallback((message: string, options?: Omit<ToastOptions, 'type'>) => {
    showToast(message, { ...options, type: 'error' })
  }, [showToast])

  const warning = useCallback((message: string, options?: Omit<ToastOptions, 'type'>) => {
    showToast(message, { ...options, type: 'warning' })
  }, [showToast])

  const info = useCallback((message: string, options?: Omit<ToastOptions, 'type'>) => {
    showToast(message, { ...options, type: 'info' })
  }, [showToast])

  return {
    showToast,
    success,
    error,
    warning,
    info
  }
}
