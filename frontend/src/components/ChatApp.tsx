import React, { useState, useCallback, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useSocket } from "../hooks/useSocket";
import { useResponsive } from "../hooks/useResponsive";
import { SocketMessage, SocketError, ModelSelectionState } from "../types";
import ModernHeader from "./ModernHeader";
import ModernChatInterface from "./ModernChatInterface";
import ModernSidebar from "./ModernSidebar";
import AuthModal from "./AuthModal";
import AdminPanel from "./AdminPanel";

type ViewMode = "chat" | "admin";

const ChatApp: React.FC = () => {
  const { isAuthenticated, user, token, login, logout, loading } = useAuth();
  const { isMobile } = useResponsive();
  const [isSidebarOpen, setIsSidebarOpen] = useState(!isMobile);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [socketMessages, setSocketMessages] = useState<SocketMessage[]>([]);
  const [currentView, setCurrentView] = useState<ViewMode>("chat");
  const [modelSelection, setModelSelection] = useState<ModelSelectionState>({
    selectedModels: ["gpt-4"],
    debateMode: "consensus",
    showDebateProcess: false,
  });

  // Auto-close sidebar on mobile when session changes
  useEffect(() => {
    if (isMobile && currentSessionId) {
      setIsSidebarOpen(false);
    }
  }, [currentSessionId, isMobile]);

  // Handle incoming Socket.IO messages
  const handleNewMessage = useCallback((message: SocketMessage) => {
    console.log("Received Socket.IO message:", message);
    setSocketMessages((prev) => [...prev, message]);
  }, []);

  // Handle Socket.IO errors
  const handleSocketError = useCallback((error: SocketError) => {
    console.error("Socket.IO error:", error);
    // TODO: Show error toast to user
  }, []);

  // Handle session creation
  const handleSessionCreated = useCallback(
    (data: { session_id: number; title: string }) => {
      console.log("Session created:", data);
      setCurrentSessionId(data.session_id.toString());
    },
    []
  );

  // Handle new chat creation
  const handleNewChat = useCallback(() => {
    setCurrentSessionId(null);
    setSocketMessages([]);
  }, []);

  // Initialize Socket.IO connection
  const { sendMessage: sendSocketMessage, isConnected: getIsConnected } =
    useSocket({
      isAuthenticated,
      token: token || undefined,
      sessionId: currentSessionId,
      onNewMessage: handleNewMessage,
      onError: handleSocketError,
      onSessionCreated: handleSessionCreated,
    });

  const isSocketConnected = getIsConnected();

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // Show loading spinner during auth initialization
  if (loading) {
    return (
      <div className="min-h-screen bg-bg-dark flex items-center justify-center">
        <div className="text-center">
          <img
            src="/logo.svg"
            alt="Consensus Agent"
            className="w-16 h-16 mx-auto mb-4 opacity-50"
          />
          <div className="text-gray-400">Loading...</div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthModal onLogin={login} />;
  }

  return (
    <div className="modern-app-layout">
      {/* Sidebar - Only show in chat mode */}
      {currentView === "chat" && (
        <ModernSidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          currentSessionId={currentSessionId}
          onSessionSelect={setCurrentSessionId}
          onNewChat={handleNewChat}
          onLogout={logout}
          currentUser={user}
          modelSelection={modelSelection}
        />
      )}

      {/* Main Content */}
      <div className="modern-main-content">
        {/* Header */}
        <ModernHeader
          onToggleSidebar={toggleSidebar}
          currentUser={user}
          isSocketConnected={isSocketConnected}
          modelSelection={modelSelection}
          onModelSelectionChange={setModelSelection}
        />

        {/* Content based on current view */}
        <div className="modern-content-area">
          {currentView === "chat" ? (
            <ModernChatInterface
              sessionId={currentSessionId}
              onSessionCreated={setCurrentSessionId}
              socketMessages={socketMessages}
              onSendSocketMessage={sendSocketMessage}
              isSocketConnected={isSocketConnected}
              modelSelection={modelSelection}
            />
          ) : (
            <AdminPanel />
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatApp;
