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

const AuthModal: React.FC<AuthModalProps> = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();
  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    setError(null);

    try {
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

        if (userResult.error) {
          console.error("User fetch error:", userResult.error);
          setError("Failed to get user information");
          apiService.clearToken();
        } else if (userResult.data) {
          console.log("Login successful, calling onLogin with:", {
            access_token: result.data.access_token,
            token_type: result.data.token_type,
            user: userResult.data,
          });
          // Pass the complete auth data to onLogin
          onLogin({
            access_token: result.data.access_token,
            token_type: result.data.token_type,
            user: userResult.data,
          });
        }
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-dark flex items-center justify-center px-4">
      <div className="bg-bg-dark-secondary border border-primary-teal/20 rounded-2xl p-8 w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <img
            src="/logo.svg"
            alt="Consensus Agent"
            className="w-16 h-16 mx-auto mb-4"
          />
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-teal to-primary-cyan bg-clip-text text-transparent mb-2">
            CONSENSUS AGENT
          </h1>
          <p className="text-gray-400 text-sm">Multi-LLM AI Chat Platform</p>
        </div>
        {/* Login Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Username Field */}
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              Username
            </label>
            <input
              {...register("username", { required: "Username is required" })}
              type="text"
              id="username"
              className="w-full px-4 py-3 bg-bg-dark border border-primary-teal/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-cyan/50 focus:border-primary-cyan text-white placeholder-gray-500"
              placeholder="Enter your username"
            />
            {errors.username && (
              <p className="text-red-400 text-sm mt-1">
                {errors.username.message || "Username is required"}
              </p>
            )}
          </div>
          {/* Password Field */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-300 mb-2"
            >
              Password
            </label>
            <input
              {...register("password", { required: "Password is required" })}
              type="password"
              id="password"
              className="w-full px-4 py-3 bg-bg-dark border border-primary-teal/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-cyan/50 focus:border-primary-cyan text-white placeholder-gray-500"
              placeholder="Enter your password"
            />
            {errors.password && (
              <p className="text-red-400 text-sm mt-1">
                {errors.password.message || "Password is required"}
              </p>
            )}
          </div>{" "}
          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              <p className="text-red-400 text-sm">
                {typeof error === "string" ? error : "An error occurred"}
              </p>
            </div>
          )}
          {/* Login Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-gradient-primary text-white font-medium py-3 px-4 rounded-lg hover:glow-effect-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        {/* Default Login Info */}
        <div className="mt-6 p-3 bg-primary-blue/10 border border-primary-blue/20 rounded-lg">
          <p className="text-primary-azure text-xs text-center">
            Default login: admin / password123
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
