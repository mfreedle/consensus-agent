import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { apiService } from "../services/api";

interface AuthModalProps {
  onLogin: (user: any) => void;
}

interface LoginForm {
  username: string;
  password: string;
}

interface RegisterForm {
  username: string;
  email?: string;
  password: string;
  confirmPassword: string;
}

type AuthMode = "login" | "register";

const AuthModal: React.FC<AuthModalProps> = ({ onLogin }) => {
  const [mode, setMode] = useState<AuthMode>("login");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<LoginForm & RegisterForm>();

  const password = watch("password");

  const switchMode = (newMode: AuthMode) => {
    setMode(newMode);
    setError(null);
    setSuccessMessage(null);
    reset();
  };

  const onSubmit = async (data: LoginForm & RegisterForm) => {
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      if (mode === "login") {
        console.log("Attempting login with:", { username: data.username });
        const result = await apiService.login({
          username: data.username,
          password: data.password,
        });

        console.log("Login result:", result);

        if (result.error) {
          console.error("Login error:", result.error);
          setError(
            typeof result.error === "string" ? result.error : "Login failed"
          );
        } else if (result.data) {
          console.log("Setting token:", result.data.access_token);
          // Set the token first
          apiService.setToken(result.data.access_token);

          // Then fetch user info
          console.log("Fetching user info...");
          const userResult = await apiService.getCurrentUser();
          console.log("User result:", userResult);

          if (userResult.data && !userResult.error) {
            // Store token in localStorage
            localStorage.setItem("auth_token", result.data.access_token);

            // Call the onLogin callback with user data and token
            onLogin({
              user: userResult.data,
              access_token: result.data.access_token,
            });
          } else {
            console.error("Failed to fetch user info:", userResult.error);
            setError("Failed to fetch user information");
          }
        }
      } else {
        // Registration
        console.log("Attempting registration with:", {
          username: data.username,
          email: data.email,
        });
        const result = await apiService.register({
          username: data.username,
          email: data.email || undefined,
          password: data.password,
        });

        console.log("Registration result:", result);

        if (result.error) {
          console.error("Registration error:", result.error);
          setError(
            typeof result.error === "string"
              ? result.error
              : "Registration failed"
          );
        } else if (result.data) {
          setSuccessMessage("Account created successfully! Please login.");
          reset();
          setMode("login");
        }
      }
    } catch (error) {
      console.error(`${mode} error:`, error);
      setError(
        `${
          mode === "login" ? "Login" : "Registration"
        } failed. Please try again.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-dark flex items-center justify-center px-4">
      <div className="bg-bg-dark-secondary border border-primary-teal/20 rounded-2xl p-6 md:p-8 w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-6 md:mb-8">
          <img
            src="/logo.svg"
            alt="Consensus Agent"
            className="w-12 h-12 md:w-16 md:h-16 mx-auto mb-3 md:mb-4"
          />
          <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-primary-teal to-primary-cyan bg-clip-text text-transparent mb-2">
            CONSENSUS AGENT
          </h1>
          <p className="text-gray-400 text-sm">Multi-LLM AI Chat Platform</p>
        </div>

        {/* Mode Toggle */}
        <div className="flex bg-bg-dark-tertiary rounded-lg p-1 mb-6">
          <button
            type="button"
            onClick={() => switchMode("login")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              mode === "login"
                ? "bg-primary-teal text-white"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => switchMode("register")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              mode === "register"
                ? "bg-primary-teal text-white"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Username Field */}
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <input
              {...registerField("username", {
                required: "Username is required",
              })}
              type="text"
              id="username"
              className="form-input"
              placeholder="Enter your username"
            />
            {errors.username && (
              <p className="text-error text-sm mt-1">
                {errors.username.message || "Username is required"}
              </p>
            )}
          </div>

          {/* Email Field (Registration only) */}
          {mode === "register" && (
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email (Optional)
              </label>
              <input
                {...registerField("email", {
                  pattern: {
                    value: /^\S+@\S+$/i,
                    message: "Please enter a valid email address",
                  },
                })}
                type="email"
                id="email"
                className="form-input"
                placeholder="Enter your email"
              />
              {errors.email && (
                <p className="text-error text-sm mt-1">
                  {errors.email.message}
                </p>
              )}
            </div>
          )}

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              {...registerField("password", {
                required: "Password is required",
                minLength:
                  mode === "register"
                    ? {
                        value: 6,
                        message: "Password must be at least 6 characters long",
                      }
                    : undefined,
              })}
              type="password"
              id="password"
              className="form-input"
              placeholder="Enter your password"
            />
            {errors.password && (
              <p className="text-error text-sm mt-1">
                {errors.password.message || "Password is required"}
              </p>
            )}
          </div>

          {/* Confirm Password Field (Registration only) */}
          {mode === "register" && (
            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">
                Confirm Password
              </label>
              <input
                {...registerField("confirmPassword", {
                  required: "Please confirm your password",
                  validate: (value) =>
                    value === password || "Passwords do not match",
                })}
                type="password"
                id="confirmPassword"
                className="form-input"
                placeholder="Confirm your password"
              />
              {errors.confirmPassword && (
                <p className="text-error text-sm mt-1">
                  {errors.confirmPassword.message}
                </p>
              )}
            </div>
          )}

          {/* Success Message */}
          {successMessage && (
            <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
              <p className="text-green-400 text-sm">{successMessage}</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              <p className="text-red-400 text-sm">
                {typeof error === "string" ? error : "An error occurred"}
              </p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="btn btn-primary w-full btn-lg"
          >
            {isLoading ? (
              <>
                <div className="loading-spinner mr-2"></div>
                {mode === "login" ? "Signing in..." : "Creating Account..."}
              </>
            ) : mode === "login" ? (
              "Sign In"
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        {/* ...existing code... */}
      </div>
    </div>
  );
};

export default AuthModal;
