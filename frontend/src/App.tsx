import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./contexts/AuthContext";
import { ErrorProvider } from "./contexts/ErrorContext";
import ErrorBoundary from "./components/ErrorBoundary";
import ChatApp from "./components/ChatApp";
import "./App.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors (client errors)
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
    mutations: {
      retry: 1, // Retry mutations once
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <ErrorProvider>
            <div className="App min-h-screen bg-bg-dark">
              {/* Skip to content link for accessibility */}
              <a href="#main-content" className="skip-link">
                Skip to main content
              </a>
              <ChatApp />
            </div>
          </ErrorProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
