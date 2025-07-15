import React, { useState, useRef, useEffect } from "react";
import { Menu, User, MoreHorizontal } from "lucide-react";
import ModernModelSelector from "./ModernModelSelector";
import { ModelSelectionState } from "../types";

interface ModernHeaderProps {
  onToggleSidebar: () => void;
  currentUser?: any;
  isSocketConnected?: boolean;
  modelSelection: ModelSelectionState;
  onModelSelectionChange: (selection: ModelSelectionState) => void;
  onProfile?: () => void;
  onLogout?: () => void;
}

const ModernHeader: React.FC<ModernHeaderProps> = ({
  onToggleSidebar,
  currentUser,
  isSocketConnected = false,
  modelSelection,
  onModelSelectionChange,
  onProfile = () => {},
  onLogout = () => {},
}) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const userButtonRef = useRef<HTMLButtonElement>(null);

  // Debug: Log when component mounts and props change
  useEffect(() => {
    console.log("ModernHeader mounted/updated", {
      onProfile: typeof onProfile,
      onLogout: typeof onLogout,
      currentUser: currentUser?.username,
    });
  }, [onProfile, onLogout, currentUser]);

  // Close menu on outside click
  useEffect(() => {
    if (!menuOpen) return;
    function handleClick(e: MouseEvent) {
      if (
        userButtonRef.current &&
        !userButtonRef.current.contains(e.target as Node)
      ) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

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
          <div className="user-section" style={{ position: "relative" }}>
            <button
              className="user-button"
              aria-label="User menu"
              onClick={() => {
                console.log(
                  "User menu button clicked, current menuOpen:",
                  menuOpen
                );
                setMenuOpen((open) => !open);
              }}
              ref={userButtonRef}
            >
              <User className="w-4 h-4" />
              <span className="user-name">{currentUser.username}</span>
              <MoreHorizontal className="w-4 h-4 text-text-muted" />
            </button>
            {menuOpen && (
              <div
                className="user-dropdown"
                style={{
                  position: "absolute",
                  right: 0,
                  top: "100%",
                  background: "#18181b",
                  border: "1px solid #333",
                  borderRadius: 6,
                  boxShadow: "0 2px 8px rgba(0,0,0,0.18)",
                  zIndex: 1000,
                  minWidth: 140,
                  marginTop: 4,
                  color: "#f3f4f6",
                }}
              >
                <button
                  className="dropdown-item"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setMenuOpen(false);
                    onProfile();
                  }}
                  style={{
                    width: "100%",
                    padding: 8,
                    textAlign: "left",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "#f3f4f6",
                  }}
                >
                  Profile
                </button>
                <button
                  className="dropdown-item"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setMenuOpen(false);
                    onLogout();
                  }}
                  style={{
                    width: "100%",
                    padding: 8,
                    textAlign: "left",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "#f3f4f6",
                  }}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

export default ModernHeader;
