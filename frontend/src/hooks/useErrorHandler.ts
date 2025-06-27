import { useState, useCallback } from 'react';

export interface AppError {
  id: string;
  type: 'network' | 'validation' | 'auth' | 'upload' | 'api' | 'unknown';
  title: string;
  message: string;
  details?: string;
  recoverable: boolean;
  timestamp: Date;
}

export interface ErrorAction {
  label: string;
  action: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
}

export const useErrorHandler = () => {
  const [errors, setErrors] = useState<AppError[]>([]);

  // Create standardized error from various sources
  const createError = useCallback((
    error: Error | string | any,
    type: AppError['type'] = 'unknown',
    context?: string
  ): AppError => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    const timestamp = new Date();

    // Handle different error types
    if (typeof error === 'string') {
      return {
        id,
        type,
        title: getErrorTitle(type),
        message: error,
        recoverable: isRecoverable(type),
        timestamp,
      };
    }

    if (error instanceof Error) {
      return {
        id,
        type,
        title: getErrorTitle(type),
        message: error.message || 'An unexpected error occurred',
        details: error.stack,
        recoverable: isRecoverable(type),
        timestamp,
      };
    }

    // Handle API errors
    if (error?.response) {
      const apiError = extractApiError(error);
      return {
        id,
        type: 'api',
        title: getErrorTitle('api'),
        message: apiError.message,
        details: apiError.details,
        recoverable: true,
        timestamp,
      };
    }

    // Fallback for unknown error structures
    return {
      id,
      type,
      title: getErrorTitle(type),
      message: 'An unexpected error occurred',
      details: context ? `Context: ${context}` : undefined,
      recoverable: isRecoverable(type),
      timestamp,
    };
  }, []);

  // Add error to the stack
  const addError = useCallback((
    error: Error | string | any,
    type: AppError['type'] = 'unknown',
    context?: string
  ) => {
    const appError = createError(error, type, context);
    setErrors(prev => [appError, ...prev.slice(0, 4)]); // Keep max 5 errors
    
    // Log error for debugging
    console.error(`[${type.toUpperCase()}] ${appError.title}:`, appError.message, appError.details);
    
    return appError.id;
  }, [createError]);

  // Remove specific error
  const removeError = useCallback((id: string) => {
    setErrors(prev => prev.filter(err => err.id !== id));
  }, []);

  // Clear all errors
  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  // Get error-specific actions
  const getErrorActions = useCallback((error: AppError): ErrorAction[] => {
    const actions: ErrorAction[] = [
      {
        label: 'Dismiss',
        action: () => removeError(error.id),
        variant: 'secondary',
      }
    ];

    switch (error.type) {
      case 'network':
        actions.unshift({
          label: 'Retry',
          action: () => {
            removeError(error.id);
            // Retry logic would be handled by the component that called addError
          },
          variant: 'primary',
        });
        break;
      
      case 'auth':
        actions.unshift({
          label: 'Login Again',
          action: () => {
            removeError(error.id);
            // Redirect to login
            window.location.reload();
          },
          variant: 'primary',
        });
        break;
      
      case 'upload':
        actions.unshift({
          label: 'Try Again',
          action: () => removeError(error.id),
          variant: 'primary',
        });
        break;
    }

    return actions;
  }, [removeError]);

  return {
    errors,
    addError,
    removeError,
    clearErrors,
    getErrorActions,
  };
};

// Helper functions
function getErrorTitle(type: AppError['type']): string {
  switch (type) {
    case 'network':
      return 'Connection Error';
    case 'validation':
      return 'Validation Error';
    case 'auth':
      return 'Authentication Error';
    case 'upload':
      return 'Upload Error';
    case 'api':
      return 'Server Error';
    default:
      return 'Error';
  }
}

function isRecoverable(type: AppError['type']): boolean {
  switch (type) {
    case 'network':
    case 'upload':
    case 'api':
      return true;
    case 'auth':
    case 'validation':
      return true;
    default:
      return false;
  }
}

function extractApiError(error: any): { message: string; details?: string } {
  // Handle different API error formats
  if (error.response?.data?.error) {
    return {
      message: error.response.data.error,
      details: error.response.data.details || `Status: ${error.response.status}`,
    };
  }

  if (error.response?.data?.message) {
    return {
      message: error.response.data.message,
      details: `Status: ${error.response.status}`,
    };
  }

  if (error.response?.status) {
    const statusMessages: Record<number, string> = {
      400: 'Bad request - please check your input',
      401: 'Authentication required - please log in',
      403: 'Access denied - insufficient permissions',
      404: 'Resource not found',
      429: 'Too many requests - please try again later',
      500: 'Server error - please try again later',
      502: 'Server temporarily unavailable',
      503: 'Service unavailable - please try again later',
    };

    return {
      message: statusMessages[error.response.status] || 'An API error occurred',
      details: `HTTP ${error.response.status}`,
    };
  }

  return {
    message: error.message || 'An unexpected API error occurred',
  };
}

// Export error types for consistency
export const ERROR_TYPES = {
  NETWORK: 'network' as const,
  VALIDATION: 'validation' as const,
  AUTH: 'auth' as const,
  UPLOAD: 'upload' as const,
  API: 'api' as const,
  UNKNOWN: 'unknown' as const,
} as const;
