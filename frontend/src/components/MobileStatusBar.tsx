import React from "react";
import { useResponsive } from "../hooks/useResponsive";

interface MobileStatusBarProps {
  isSocketConnected: boolean;
  currentUser?: any;
  modelSelection?: {
    selectedModels: string[];
    debateMode: string;
  };
}

export const MobileStatusBar: React.FC<MobileStatusBarProps> = ({
  isSocketConnected,
  currentUser,
  modelSelection,
}) => {
  const { isMobile } = useResponsive();

  if (!isMobile) return null;

  return (
    <div className="bg-bg-dark-secondary border-b border-primary-teal/20 px-4 py-2 flex items-center justify-between text-xs">
      {/* User Info */}
      <div className="flex items-center space-x-2">
        <div className="w-1.5 h-1.5 bg-primary-cyan rounded-full"></div>
        <span className="text-gray-300">
          {currentUser?.username || "Guest"}
        </span>
      </div>

      {/* Status Indicators */}
      <div className="flex items-center space-x-3">
        {/* Model Status */}
        <div className="flex items-center space-x-1">
          <div className="w-1.5 h-1.5 bg-primary-green rounded-full animate-pulse"></div>
          <span className="text-gray-400">
            {modelSelection?.selectedModels?.length || 1}M
          </span>
        </div>

        {/* Connection Status */}
        <div className="flex items-center space-x-1">
          <div
            className={`w-1.5 h-1.5 rounded-full ${
              isSocketConnected
                ? "bg-primary-green animate-pulse"
                : "bg-red-500"
            }`}
          ></div>
          <span
            className={`${
              isSocketConnected ? "text-primary-green" : "text-red-400"
            }`}
          >
            {isSocketConnected ? "RT" : "HTTP"}
          </span>
        </div>
      </div>
    </div>
  );
};

export default MobileStatusBar;
