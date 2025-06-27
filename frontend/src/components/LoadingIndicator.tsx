import React from "react";
import { Loader2 } from "lucide-react";

export interface LoadingState {
  isLoading: boolean;
  message?: string;
  subMessage?: string;
  progress?: number; // 0-100
  variant?: "default" | "overlay" | "inline" | "skeleton";
}

interface LoadingIndicatorProps extends LoadingState {
  className?: string;
  size?: "sm" | "md" | "lg";
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  isLoading,
  message = "Loading...",
  subMessage,
  progress,
  variant = "default",
  size = "md",
  className = "",
}) => {
  if (!isLoading) return null;

  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };

  const textSizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg",
  };

  if (variant === "overlay") {
    return (
      <div
        className={`fixed inset-0 bg-black/50 z-50 flex items-center justify-center ${className}`}
      >
        <div className="bg-bg-dark-secondary border border-gray-600 rounded-lg p-6 max-w-sm mx-4">
          <div className="flex flex-col items-center text-center">
            <Loader2
              className={`${sizeClasses[size]} text-primary-cyan animate-spin mb-4`}
            />
            <h3
              className={`${textSizeClasses[size]} font-medium text-white mb-2`}
            >
              {message}
            </h3>
            {subMessage && (
              <p className="text-sm text-gray-400 mb-4">{subMessage}</p>
            )}
            {progress !== undefined && (
              <div className="w-full">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Progress</span>
                  <span>{Math.round(progress)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-primary-cyan h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (variant === "inline") {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <Loader2
          className={`${sizeClasses[size]} text-primary-cyan animate-spin`}
        />
        <span className={`${textSizeClasses[size]} text-gray-300`}>
          {message}
        </span>
      </div>
    );
  }

  if (variant === "skeleton") {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="space-y-3">
          <div className="h-4 bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2"></div>
          <div className="h-4 bg-gray-700 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  // Default variant
  return (
    <div
      className={`flex flex-col items-center justify-center p-6 ${className}`}
    >
      <Loader2
        className={`${sizeClasses[size]} text-primary-cyan animate-spin mb-4`}
      />
      <h3 className={`${textSizeClasses[size]} font-medium text-white mb-2`}>
        {message}
      </h3>
      {subMessage && (
        <p className="text-sm text-gray-400 mb-4 text-center max-w-sm">
          {subMessage}
        </p>
      )}
      {progress !== undefined && (
        <div className="w-full max-w-sm">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-primary-cyan h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

// Hook for managing loading states
export const useLoadingState = (initialState: boolean = false) => {
  const [loadingState, setLoadingState] = React.useState<LoadingState>({
    isLoading: initialState,
  });

  const setLoading = React.useCallback(
    (
      isLoading: boolean,
      message?: string,
      subMessage?: string,
      progress?: number
    ) => {
      setLoadingState({
        isLoading,
        message,
        subMessage,
        progress,
      });
    },
    []
  );

  const updateProgress = React.useCallback((progress: number) => {
    setLoadingState((prev) => ({ ...prev, progress }));
  }, []);

  const updateMessage = React.useCallback(
    (message: string, subMessage?: string) => {
      setLoadingState((prev) => ({ ...prev, message, subMessage }));
    },
    []
  );

  return {
    ...loadingState,
    setLoading,
    updateProgress,
    updateMessage,
  };
};

export default LoadingIndicator;
