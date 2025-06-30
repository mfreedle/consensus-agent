import React from "react";
import { Menu, LogOut, Settings, MessageSquare } from "lucide-react";
import Tooltip from "./Tooltip";

interface HeaderProps {
  onToggleSidebar: () => void;
  onLogout: () => void;
  currentUser?: any;
  isSocketConnected?: boolean;
  currentView?: "chat" | "admin";
  onViewChange?: (view: "chat" | "admin") => void;
}

const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  onLogout,
  currentUser,
  isSocketConnected = false,
  currentView = "chat",
  onViewChange,
}) => {
  return (
    <div className="flex items-center justify-between w-full">
      {/* Left Section */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onToggleSidebar}
          className="btn btn-ghost btn-sm lg:hidden"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-4 h-4" />
        </button>

        {/* Logo and Title - Compact */}
        <div className="flex items-center space-x-2">
          <img src="/logo.svg" alt="Consensus Agent" className="w-6 h-6" />
          <h1 className="text-lg font-bold bg-gradient-to-r from-primary-teal to-primary-cyan bg-clip-text text-transparent hidden sm:block">
            CONSENSUS AGENT
          </h1>
          <h1 className="text-lg font-bold bg-gradient-to-r from-primary-teal to-primary-cyan bg-clip-text text-transparent sm:hidden">
            CA
          </h1>
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center space-x-2">
        {/* User Info - Compact */}
        {currentUser && (
          <div className="text-sm text-text-secondary hidden md:block">
            <span className="text-text-accent font-medium">
              {currentUser.username}
            </span>
          </div>
        )}

        {/* Connection Status - Enhanced */}
        <Tooltip
          content={
            isSocketConnected
              ? "Real-time connection active"
              : "Connection unavailable"
          }
        >
          <div
            className={`status-indicator ${
              isSocketConnected ? "status-success" : "status-error"
            }`}
          >
            <div
              className={`w-2 h-2 rounded-full ${
                isSocketConnected ? "bg-success animate-pulse" : "bg-error"
              }`}
            ></div>
            <span className="hidden sm:inline">
              {isSocketConnected ? "Connected" : "Offline"}
            </span>
          </div>
        </Tooltip>

        {/* View Switcher - Compact */}
        {onViewChange && (
          <div className="flex items-center bg-bg-dark-secondary border border-bg-hover rounded-lg p-1">
            <button
              onClick={() => onViewChange("chat")}
              className={`btn btn-sm ${
                currentView === "chat" ? "btn-primary" : "btn-ghost"
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span className="hidden sm:inline ml-1">Chat</span>
            </button>
            <button
              onClick={() => onViewChange("admin")}
              className={`btn btn-sm ${
                currentView === "admin"
                  ? "bg-primary-blue text-white"
                  : "btn-ghost"
              }`}
            >
              <Settings className="w-4 h-4" />
              <span className="hidden sm:inline ml-1">Admin</span>
            </button>
          </div>
        )}

        {/* Logout Button - Compact */}
        <Tooltip content="Sign out">
          <button
            onClick={onLogout}
            className="btn btn-sm btn-danger"
            aria-label="Logout"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline ml-1">Logout</span>
          </button>
        </Tooltip>
      </div>
    </div>
  );
};

export default Header;
