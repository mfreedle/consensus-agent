import React, { useState, useEffect, useCallback } from "react";
import {
  X,
  AlertTriangle,
  AlertCircle,
  Wifi,
  Upload,
  Shield,
  Zap,
} from "lucide-react";
import { AppError } from "../hooks/useErrorHandler";
import { useError } from "../contexts/ErrorContext";

interface ErrorToastProps {
  error: AppError;
}

const ErrorToast: React.FC<ErrorToastProps> = ({ error }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  const { removeError, getErrorActions } = useError();

  const handleDismiss = useCallback(() => {
    setIsExiting(true);
    setTimeout(() => {
      removeError(error.id);
    }, 300);
  }, [removeError, error.id]);

  useEffect(() => {
    // Trigger animation on mount
    setIsVisible(true);

    // Auto-dismiss after 8 seconds for recoverable errors
    if (error.recoverable) {
      const timer = setTimeout(() => {
        handleDismiss();
      }, 8000);

      return () => clearTimeout(timer);
    }
  }, [error.recoverable, handleDismiss]);

  const getErrorIcon = () => {
    switch (error.type) {
      case "network":
        return <Wifi className="w-5 h-5" />;
      case "upload":
        return <Upload className="w-5 h-5" />;
      case "auth":
        return <Shield className="w-5 h-5" />;
      case "api":
        return <Zap className="w-5 h-5" />;
      case "validation":
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <AlertTriangle className="w-5 h-5" />;
    }
  };

  const getErrorColor = () => {
    switch (error.type) {
      case "auth":
        return "border-red-500/50 bg-red-500/10 text-red-400";
      case "network":
        return "border-orange-500/50 bg-orange-500/10 text-orange-400";
      case "upload":
        return "border-blue-500/50 bg-blue-500/10 text-blue-400";
      case "validation":
        return "border-yellow-500/50 bg-yellow-500/10 text-yellow-400";
      default:
        return "border-red-500/50 bg-red-500/10 text-red-400";
    }
  };

  const actions = getErrorActions(error);

  return (
    <div
      className={`
        transform transition-all duration-300 ease-out
        ${
          isVisible && !isExiting
            ? "translate-x-0 opacity-100"
            : "translate-x-full opacity-0"
        }
      `}
    >
      <div
        className={`
        border rounded-lg p-4 backdrop-blur-sm
        ${getErrorColor()}
        bg-bg-dark-secondary border-opacity-50
        shadow-lg max-w-sm
      `}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className={`${getErrorColor().split(" ")[2]}`}>
              {getErrorIcon()}
            </div>
            <h4 className="font-medium text-white text-sm">{error.title}</h4>
          </div>
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 p-1 rounded hover:bg-gray-700 transition-colors"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        {/* Message */}
        <p className="text-sm text-gray-300 mb-3 leading-relaxed">
          {error.message}
        </p>

        {/* Details (Development only) */}
        {process.env.NODE_ENV === "development" && error.details && (
          <details className="mb-3">
            <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-300">
              Show Details
            </summary>
            <pre className="text-xs text-gray-500 mt-1 p-2 bg-gray-800/50 rounded border border-gray-600 overflow-auto max-h-20">
              {error.details}
            </pre>
          </details>
        )}

        {/* Actions */}
        {actions.length > 0 && (
          <div className="flex items-center space-x-2">
            {actions.map((action, index) => (
              <button
                key={index}
                onClick={action.action}
                className={`
                  px-3 py-1 text-xs font-medium rounded transition-colors
                  ${
                    action.variant === "primary"
                      ? "bg-primary-teal hover:bg-primary-teal/80 text-white"
                      : action.variant === "danger"
                      ? "bg-red-500 hover:bg-red-600 text-white"
                      : "bg-gray-600 hover:bg-gray-500 text-gray-200"
                  }
                `}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}

        {/* Auto-dismiss progress bar */}
        {error.recoverable && (
          <div className="mt-3 h-1 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-teal rounded-full transition-all ease-linear"
              style={{
                width: isVisible ? "0%" : "100%",
                transition: isVisible ? "width 8s linear" : "none",
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ErrorToast;
