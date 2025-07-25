import React from "react";
import { Menu } from "lucide-react";
import ModernModelSelector from "./ModernModelSelector";
import { ModelSelectionState } from "../types";

interface ModernHeaderProps {
  onToggleSidebar: () => void;
  isSocketConnected?: boolean;
  modelSelection?: ModelSelectionState;
  onModelSelectionChange?: (selection: ModelSelectionState) => void;
}

const ModernHeader: React.FC<ModernHeaderProps> = ({
  onToggleSidebar,
  isSocketConnected = false,
  modelSelection,
  onModelSelectionChange,
}) => {
  return (
    <header className="modern-header">
      <div className="header-content">
        {/* Left Section - Hamburger Menu */}
        <div className="header-left">
          <button
            className="sidebar-toggle"
            onClick={onToggleSidebar}
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>
          <h1 className="app-title">Consensus Agent</h1>
        </div>

        {/* Center Section - Model Selection */}
        <div className="header-center">
          {modelSelection && onModelSelectionChange && (
            <ModernModelSelector
              modelSelection={modelSelection}
              onModelSelectionChange={onModelSelectionChange}
            />
          )}
        </div>

        {/* Right Section - Connection Status */}
        <div className="header-right">
          <div
            className={`connection-status ${
              isSocketConnected ? "connected" : "offline"
            }`}
          >
            <div className="status-dot" />
            <span className="status-text">
              {isSocketConnected ? "Connected" : "Offline"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default ModernHeader;
