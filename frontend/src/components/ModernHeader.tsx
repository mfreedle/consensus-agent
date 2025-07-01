import React from "react";
import { Menu, User, MoreHorizontal } from "lucide-react";
import ModernModelSelector from "./ModernModelSelector";
import { ModelSelectionState } from "../types";

interface ModernHeaderProps {
  onToggleSidebar: () => void;
  currentUser?: any;
  isSocketConnected?: boolean;
  modelSelection: ModelSelectionState;
  onModelSelectionChange: (selection: ModelSelectionState) => void;
}

const ModernHeader: React.FC<ModernHeaderProps> = ({
  onToggleSidebar,
  currentUser,
  isSocketConnected = false,
  modelSelection,
  onModelSelectionChange,
}) => {
  return (
    <header className="modern-header">
      {/* Left Section */}
      <div className="header-left">
        <button
          onClick={onToggleSidebar}
          className="sidebar-toggle"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="logo-section">
          <div className="logo">CA</div>
          <h1 className="app-title">
            <span className="title-main">Consensus Agent</span>
            <span className="title-subtitle">Multi-LLM AI Platform</span>
          </h1>
        </div>
      </div>

      {/* Center Section - Model Selector */}
      <div className="header-center">
        <ModernModelSelector
          modelSelection={modelSelection}
          onModelSelectionChange={onModelSelectionChange}
        />
      </div>

      {/* Right Section */}
      <div className="header-right">
        {/* Connection Status */}
        <div
          className={`connection-status ${
            isSocketConnected ? "connected" : "disconnected"
          }`}
        >
          <div className="status-dot" />
          <span className="status-text">
            {isSocketConnected ? "Connected" : "Offline"}
          </span>
        </div>

        {/* User Menu */}
        {currentUser && (
          <div className="user-section">
            <button className="user-button" aria-label="User menu">
              <User className="w-4 h-4" />
              <span className="user-name">{currentUser.username}</span>
              <MoreHorizontal className="w-4 h-4 text-text-muted" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default ModernHeader;
