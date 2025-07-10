import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { apiService } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

interface PasswordChangeForm {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface ProfileUpdateForm {
  email?: string;
}

interface UserSettingsProps {
  onClose: () => void;
}

const UserSettings: React.FC<UserSettingsProps> = ({ onClose }) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<"profile" | "password">("profile");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
  } = useForm<ProfileUpdateForm>({
    defaultValues: {
      email: user?.email || "",
    },
  });

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors },
    reset: resetPassword,
    watch,
  } = useForm<PasswordChangeForm>();

  const newPassword = watch("new_password");

  const onProfileSubmit = async (data: ProfileUpdateForm) => {
    setIsLoading(true);
    setMessage(null);

    try {
      const result = await apiService.updateProfile({
        email: data.email || undefined,
      });

      if (result.error) {
        setMessage({ type: "error", text: result.error });
      } else {
        setMessage({ type: "success", text: "Profile updated successfully!" });
      }
    } catch (error) {
      setMessage({
        type: "error",
        text: "Failed to update profile. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const onPasswordSubmit = async (data: PasswordChangeForm) => {
    setIsLoading(true);
    setMessage(null);

    try {
      const result = await apiService.changePassword({
        current_password: data.current_password,
        new_password: data.new_password,
      });

      if (result.error) {
        setMessage({ type: "error", text: result.error });
      } else {
        setMessage({ type: "success", text: "Password changed successfully!" });
        resetPassword();
      }
    } catch (error) {
      setMessage({
        type: "error",
        text: "Failed to change password. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-bg-dark-secondary border border-border-dark rounded-lg p-6 w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-text-primary">
            Account Settings
          </h2>
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* User Info */}
        <div className="mb-6 p-4 bg-bg-dark-tertiary rounded-lg">
          <h3 className="text-sm font-medium text-text-secondary mb-1">
            Logged in as
          </h3>
          <p className="text-lg font-semibold text-text-primary">
            {user?.username}
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex bg-bg-dark-tertiary rounded-lg p-1 mb-6">
          <button
            type="button"
            onClick={() => setActiveTab("profile")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === "profile"
                ? "bg-primary-blue text-white"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Profile
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("password")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === "password"
                ? "bg-primary-blue text-white"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Password
          </button>
        </div>

        {/* Profile Tab */}
        {activeTab === "profile" && (
          <form
            onSubmit={handleProfileSubmit(onProfileSubmit)}
            className="space-y-4"
          >
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email
              </label>
              <input
                {...registerProfile("email", {
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
              {profileErrors.email && (
                <p className="text-error text-sm mt-1">
                  {profileErrors.email.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? (
                <>
                  <div className="loading-spinner mr-2"></div>
                  Updating Profile...
                </>
              ) : (
                "Update Profile"
              )}
            </button>
          </form>
        )}

        {/* Password Tab */}
        {activeTab === "password" && (
          <form
            onSubmit={handlePasswordSubmit(onPasswordSubmit)}
            className="space-y-4"
          >
            <div className="form-group">
              <label htmlFor="current_password" className="form-label">
                Current Password
              </label>
              <input
                {...registerPassword("current_password", {
                  required: "Current password is required",
                })}
                type="password"
                id="current_password"
                className="form-input"
                placeholder="Enter your current password"
              />
              {passwordErrors.current_password && (
                <p className="text-error text-sm mt-1">
                  {passwordErrors.current_password.message}
                </p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="new_password" className="form-label">
                New Password
              </label>
              <input
                {...registerPassword("new_password", {
                  required: "New password is required",
                  minLength: {
                    value: 6,
                    message: "Password must be at least 6 characters long",
                  },
                })}
                type="password"
                id="new_password"
                className="form-input"
                placeholder="Enter your new password"
              />
              {passwordErrors.new_password && (
                <p className="text-error text-sm mt-1">
                  {passwordErrors.new_password.message}
                </p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="confirm_password" className="form-label">
                Confirm New Password
              </label>
              <input
                {...registerPassword("confirm_password", {
                  required: "Please confirm your new password",
                  validate: (value) =>
                    value === newPassword || "Passwords do not match",
                })}
                type="password"
                id="confirm_password"
                className="form-input"
                placeholder="Confirm your new password"
              />
              {passwordErrors.confirm_password && (
                <p className="text-error text-sm mt-1">
                  {passwordErrors.confirm_password.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? (
                <>
                  <div className="loading-spinner mr-2"></div>
                  Changing Password...
                </>
              ) : (
                "Change Password"
              )}
            </button>
          </form>
        )}

        {/* Message Display */}
        {message && (
          <div
            className={`mt-4 p-3 rounded-lg border ${
              message.type === "success"
                ? "bg-green-500/10 border-green-500/20"
                : "bg-red-500/10 border-red-500/20"
            }`}
          >
            <p
              className={`text-sm ${
                message.type === "success" ? "text-green-400" : "text-red-400"
              }`}
            >
              {message.text}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserSettings;
