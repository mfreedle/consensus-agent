import React, { useState, useCallback, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useSocket } from "../hooks/useSocket";
import { useResponsive } from "../hooks/useResponsive";
import { SocketMessage, SocketError, ModelSelectionState } from "../types";
import Header from "./Header";
import ChatInterface from "./ChatInterface";
import Sidebar from "./Sidebar";
import AuthModal from "./AuthModal";
import MobileStatusBar from "./MobileStatusBar";
import AdminPanel from "./AdminPanel";

type ViewMode = "chat" | "admin";

const ChatApp: React.FC = () => {
  const { isAuthenticated, user, token, login, logout, loading } = useAuth();
  const { isMobile } = useResponsive();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [socketMessages, setSocketMessages] = useState<SocketMessage[]>([]);
  const [currentView, setCurrentView] = useState<ViewMode>("chat");
  const [modelSelection, setModelSelection] = useState<ModelSelectionState>({
    selectedModels: [],
    debateMode: "consensus",
    showDebateProcess: true,
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
    <div className="flex h-screen bg-bg-dark text-white">
      {/* Sidebar - Only show in chat mode */}
      {currentView === "chat" && (
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          currentSessionId={currentSessionId}
          onSessionSelect={setCurrentSessionId}
          modelSelection={modelSelection}
          onModelSelectionChange={setModelSelection}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header
          onToggleSidebar={toggleSidebar}
          onLogout={logout}
          currentUser={user}
          isSocketConnected={isSocketConnected}
          currentView={currentView}
          onViewChange={setCurrentView}
        />

        {/* Mobile Status Bar - Only in chat mode */}
        {currentView === "chat" && (
          <MobileStatusBar
            isSocketConnected={isSocketConnected}
            currentUser={user}
            modelSelection={modelSelection}
          />
        )}

        {/* Content based on current view */}
        {currentView === "chat" ? (
          <ChatInterface
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
  );
};

export default ChatApp;
