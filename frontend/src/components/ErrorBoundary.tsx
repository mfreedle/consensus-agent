import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);

    this.setState({
      error,
      errorInfo,
    });

    // Here you could send error to logging service
    // logErrorToService(error, errorInfo);
  }

  private handleRefresh = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = "/";
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-bg-dark flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center">
            <div className="bg-bg-dark-secondary border border-red-500/20 rounded-lg p-6">
              {/* Error Icon */}
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-red-500/10 rounded-full">
                  <AlertTriangle className="w-8 h-8 text-red-400" />
                </div>
              </div>

              {/* Error Title */}
              <h2 className="text-xl font-semibold text-white mb-2">
                Something went wrong
              </h2>

              {/* Error Message */}
              <p className="text-gray-400 mb-6">
                The application encountered an unexpected error. This has been
                logged for our review.
              </p>

              {/* Error Details (Development Only) */}
              {process.env.NODE_ENV === "development" && this.state.error && (
                <div className="mb-6 p-4 bg-gray-800/50 rounded-lg border border-gray-600 text-left">
                  <h4 className="text-sm font-medium text-red-400 mb-2">
                    Error Details (Development)
                  </h4>
                  <pre className="text-xs text-gray-300 overflow-auto">
                    {this.state.error.toString()}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={this.handleRefresh}
                  className="flex items-center justify-center px-4 py-2 bg-primary-teal hover:bg-primary-teal/80 text-white rounded-lg transition-colors"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reload Page
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="flex items-center justify-center px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Go Home
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
