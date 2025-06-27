import React, { createContext, useContext, ReactNode } from "react";
import {
  useErrorHandler,
  AppError,
  ErrorAction,
} from "../hooks/useErrorHandler";
import ErrorToast from "../components/ErrorToast";

interface ErrorContextType {
  errors: AppError[];
  addError: (
    error: Error | string | any,
    type?: AppError["type"],
    context?: string
  ) => string;
  removeError: (id: string) => void;
  clearErrors: () => void;
  getErrorActions: (error: AppError) => ErrorAction[];
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

interface ErrorProviderProps {
  children: ReactNode;
}

export const ErrorProvider: React.FC<ErrorProviderProps> = ({ children }) => {
  const errorHandler = useErrorHandler();

  return (
    <ErrorContext.Provider value={errorHandler}>
      {children}
      <ErrorToastContainer errors={errorHandler.errors} />
    </ErrorContext.Provider>
  );
};

export const useError = (): ErrorContextType => {
  const context = useContext(ErrorContext);
  if (context === undefined) {
    throw new Error("useError must be used within an ErrorProvider");
  }
  return context;
};

// Error Toast Container Component
interface ErrorToastContainerProps {
  errors: AppError[];
}

const ErrorToastContainer: React.FC<ErrorToastContainerProps> = ({
  errors,
}) => {
  if (errors.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {errors.slice(0, 3).map((error) => (
        <ErrorToast key={error.id} error={error} />
      ))}
    </div>
  );
};
