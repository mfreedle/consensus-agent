import React, { useState, useEffect } from "react";
import {
  Plus,
  MessageSquare,
  Settings,
  MoreHorizontal,
  User,
  LogOut,
  Zap,
  Brain,
  Shuffle,
  Trash2,
} from "lucide-react";
import { apiService, ChatSession } from "../services/api";
import { ModelSelectionState } from "../types";

interface ModernSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onNewChat: () => void;
  onLogout?: () => void;
  onSettings?: () => void;
  currentUser?: any;
  modelSelection?: ModelSelectionState;
}

// Helper function to get consensus mode icon
const getConsensusIcon = (models: string[], debateMode: string) => {
  if (models.length === 0) return null;
  if (models.length === 1) return <Zap className="w-3 h-3 text-primary-cyan" />;
  if (debateMode === "consensus")
    return <Brain className="w-3 h-3 text-primary-teal" />;
  return <Shuffle className="w-3 h-3 text-primary-blue" />;
};

// Helper function to format relative time
const getRelativeTime = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInHours = Math.floor(
    (now.getTime() - date.getTime()) / (1000 * 60 * 60)
  );

  if (diffInHours < 1) return "now";
  if (diffInHours < 24) return `${diffInHours}h`;
  if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d`;
  return date.toLocaleDateString();
};

const ModernSidebar: React.FC<ModernSidebarProps> = ({
  isOpen,
  onClose,
  currentSessionId,
  onSessionSelect,
  onNewChat,
  onLogout,
  onSettings,
  currentUser,
  modelSelection = {
    selectedModels: [],
    debateMode: "consensus",
    showDebateProcess: true,
  },
}) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setIsLoading(true);
    try {
      const result = await apiService.getChatSessions();
      if (result.data) {
        setSessions(result.data);
      }
    } catch (error) {
      console.error("Failed to load sessions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const result = await apiService.createChatSession();
      if (result.data) {
        setSessions((prev) => [result.data!, ...prev]);
        onSessionSelect(result.data.id.toString());
        onNewChat();
      }
    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
  };

  const handleDeleteSession = async (
    sessionId: number,
    event: React.MouseEvent
  ) => {
    // Prevent the session from being selected when delete is clicked
    event.stopPropagation();

    // Confirm deletion
    if (
      !window.confirm(
        "Are you sure you want to delete this conversation? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      await apiService.deleteChatSession(sessionId);

      // Remove session from local state
      setSessions((prev) => prev.filter((session) => session.id !== sessionId));

      // If this was the current session, clear it
      if (currentSessionId === sessionId.toString()) {
        onSessionSelect("");
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
      alert("Failed to delete conversation. Please try again.");
    }
  };

  return (
    <>
      {/* Mobile Overlay */}
      <div
        className={`mobile-overlay ${isOpen ? "active" : ""}`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modern Sidebar */}
      <nav
        className={`modern-sidebar ${isOpen ? "mobile-open" : ""}`}
        role="navigation"
        aria-label="Chat navigation"
      >
        {/* New Chat Button */}
        <div className="sidebar-header">
          <button
            onClick={handleNewChat}
            className="new-chat-button"
            aria-label="Start new chat"
          >
            <Plus className="w-4 h-4" />
            <span>New chat</span>
          </button>
        </div>

        {/* Chat History */}
        <div className="chat-history">
          {isLoading ? (
            <div className="loading-chats">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="chat-item-skeleton" />
              ))}
            </div>
          ) : sessions.length === 0 ? (
            <div className="empty-chats">
              <MessageSquare className="w-8 h-8 text-text-muted mx-auto mb-2" />
              <p className="text-xs text-text-muted text-center">
                No conversations yet
              </p>
            </div>
          ) : (
            <div className="chat-list">
              {sessions.map((session) => {
                const isActive = currentSessionId === session.id.toString();
                const consensusIcon = getConsensusIcon(
                  modelSelection.selectedModels,
                  modelSelection.debateMode
                );

                return (
                  <div
                    key={session.id}
                    className={`chat-item ${isActive ? "active" : ""}`}
                  >
                    <button
                      onClick={() => onSessionSelect(session.id.toString())}
                      className="chat-item-main"
                      aria-label={`Open chat: ${session.title || "Untitled"}`}
                    >
                      <div className="chat-item-content">
                        <div className="chat-item-header">
                          {consensusIcon && (
                            <span className="consensus-icon">
                              {consensusIcon}
                            </span>
                          )}
                          <span className="chat-title">
                            {session.title || "New conversation"}
                          </span>
                        </div>
                        <span className="chat-time">
                          {getRelativeTime(session.created_at)}
                        </span>
                      </div>

                      {isActive && (
                        <div className="active-indicator" aria-hidden="true" />
                      )}
                    </button>

                    <button
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      className="chat-item-delete"
                      aria-label={`Delete chat: ${session.title || "Untitled"}`}
                      title="Delete conversation"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="sidebar-footer">
          {currentUser && (
            <div className="user-menu-container">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="user-menu-trigger"
                aria-expanded={showUserMenu}
                aria-label="User menu"
              >
                <div className="user-info">
                  <User className="w-4 h-4" />
                  <span className="username">{currentUser.username}</span>
                </div>
                <MoreHorizontal className="w-4 h-4 text-text-muted" />
              </button>

              {showUserMenu && (
                <div className="user-menu-dropdown">
                  {onSettings && (
                    <button onClick={onSettings} className="menu-item">
                      <Settings className="w-4 h-4" />
                      Settings
                    </button>
                  )}
                  {onLogout && (
                    <button
                      onClick={onLogout}
                      className="menu-item menu-item-danger"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign out
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </nav>
    </>
  );
};

export default ModernSidebar;
