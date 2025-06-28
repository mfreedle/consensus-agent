import React from "react";
import { Menu, LogOut } from "lucide-react";

interface HeaderProps {
  onToggleSidebar: () => void;
  onLogout: () => void;
  currentUser?: any;
  isSocketConnected?: boolean;
}

const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  onLogout,
  currentUser,
  isSocketConnected = false,
}) => {
  return (
    <header className="bg-bg-dark-secondary border-b border-primary-teal/20 px-4 md:px-6 py-3 md:py-4 flex items-center justify-between">
      {/* Left Section */}
      <div className="flex items-center space-x-2 md:space-x-4">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg hover:bg-primary-teal/10 transition-colors"
        >
          <Menu className="w-5 h-5 text-primary-cyan" />
        </button>

        {/* Logo and Title */}
        <div className="flex items-center space-x-2 md:space-x-3">
          <img
            src="/logo.svg"
            alt="Consensus Agent"
            className="w-6 h-6 md:w-8 md:h-8"
          />
          <h1 className="text-lg md:text-xl font-bold bg-gradient-to-r from-primary-teal to-primary-cyan bg-clip-text text-transparent hidden sm:block">
            CONSENSUS AGENT
          </h1>
          <h1 className="text-lg font-bold bg-gradient-to-r from-primary-teal to-primary-cyan bg-clip-text text-transparent sm:hidden">
            CA
          </h1>
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center space-x-2 md:space-x-4">
        {/* User Info - Hidden on small screens */}
        {currentUser && (
          <div className="text-sm text-gray-300 hidden lg:block">
            Welcome,{" "}
            <span className="text-primary-cyan font-medium">
              {currentUser.username}
            </span>
          </div>
        )}

        {/* Status Indicators - Responsive */}
        <div className="flex items-center space-x-1 md:space-x-2">
          {/* Socket Connection Status */}
          <div
            className={`flex items-center space-x-1 md:space-x-2 px-2 md:px-3 py-1 rounded-full ${
              isSocketConnected ? "bg-primary-green/10" : "bg-red-500/10"
            }`}
          >
            <div
              className={`w-2 h-2 rounded-full ${
                isSocketConnected
                  ? "bg-primary-green animate-pulse"
                  : "bg-red-500"
              }`}
            ></div>
            <span
              className={`text-xs md:text-sm hidden sm:inline ${
                isSocketConnected ? "text-primary-green" : "text-red-400"
              }`}
            >
              {isSocketConnected ? "Connected" : "Connecting..."}
            </span>
          </div>

          {/* Model Status Indicator - Compact on mobile */}
          <div className="flex items-center space-x-1 md:space-x-2 px-2 md:px-3 py-1 bg-primary-teal/10 rounded-full">
            <div className="w-2 h-2 bg-primary-green rounded-full animate-pulse"></div>
            <span className="text-xs md:text-sm text-primary-cyan hidden sm:inline">
              Multi-LLM
            </span>
            <span className="text-xs md:text-sm text-primary-cyan hidden md:inline">
              Active
            </span>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={onLogout}
          className="p-2 rounded-lg hover:bg-red-500/10 transition-colors group"
          title="Logout"
        >
          <LogOut className="w-5 h-5 text-gray-400 group-hover:text-red-400" />
        </button>
      </div>
    </header>
  );
};

export default Header;
