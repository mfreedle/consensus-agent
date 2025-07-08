import React, { useState, useCallback, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useSocket } from "../hooks/useSocket";
import { useResponsive } from "../hooks/useResponsive";
import {
  SocketMessage,
  SocketError,
  ProcessingStatus,
  ModelSelectionState,
} from "../types";
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
  const [processingStatus, setProcessingStatus] =
    useState<ProcessingStatus | null>(null);
  const [currentView, setCurrentView] = useState<ViewMode>("chat");
  const [modelSelection, setModelSelection] = useState<ModelSelectionState>({
    selectedModels: ["gpt-4.1"], // Use one of our curated models
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

    // Clear processing status when we receive a response
    if (message.role === "assistant") {
      setProcessingStatus(null);
    }
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

  // Handle processing status updates
  const handleProcessingStatus = useCallback(
    (status: ProcessingStatus) => {
      console.log("Processing status:", status);
      // Update status for the current session
      if (status.session_id.toString() === currentSessionId) {
        setProcessingStatus(status);
      }
    },
    [currentSessionId]
  );

  // Handle session selection with cleanup
  const handleSessionSelect = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId);
    setSocketMessages([]); // Clear socket messages when switching sessions
  }, []);

  // Handle new chat creation
  const handleNewChat = useCallback(() => {
    setCurrentSessionId(null);
    setSocketMessages([]); // Clear socket messages for new chat
  }, []);

  // Handle settings navigation
  const handleSettings = useCallback(() => {
    setCurrentView("admin");
  }, []);

  // Handle back to chat navigation
  const handleBackToChat = useCallback(() => {
    setCurrentView("chat");
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
      onProcessingStatus: handleProcessingStatus,
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
          onSessionSelect={handleSessionSelect}
          onNewChat={handleNewChat}
          onLogout={logout}
          onSettings={handleSettings}
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
              processingStatus={processingStatus}
            />
          ) : (
            <AdminPanel onBack={handleBackToChat} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatApp;
