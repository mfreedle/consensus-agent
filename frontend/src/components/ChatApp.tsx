import React, { useState, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useSocket } from "../hooks/useSocket";
import { SocketMessage, SocketError, ModelSelectionState } from "../types";
import Header from "./Header";
import ChatInterface from "./ChatInterface";
import Sidebar from "./Sidebar";
import AuthModal from "./AuthModal";

const ChatApp: React.FC = () => {
  const { isAuthenticated, user, token, login, logout, loading } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [socketMessages, setSocketMessages] = useState<SocketMessage[]>([]);
  const [modelSelection, setModelSelection] = useState<ModelSelectionState>({
    selectedModels: [],
    debateMode: "consensus",
    showDebateProcess: true,
  });

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
  // Initialize Socket.IO connection
  const { sendMessage: sendSocketMessage, isConnected: getIsConnected } =
    useSocket({
      isAuthenticated,
      token: token || undefined,
      sessionId: currentSessionId,
      onNewMessage: handleNewMessage,
      onError: handleSocketError,
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
      {/* Sidebar */}{" "}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        currentSessionId={currentSessionId}
        onSessionSelect={setCurrentSessionId}
        modelSelection={modelSelection}
        onModelSelectionChange={setModelSelection}
      />
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}{" "}
        <Header
          onToggleSidebar={toggleSidebar}
          onLogout={logout}
          currentUser={user}
          isSocketConnected={isSocketConnected}
        />
        {/* Chat Interface */}
        <ChatInterface
          sessionId={currentSessionId}
          onSessionCreated={setCurrentSessionId}
          socketMessages={socketMessages}
          onSendSocketMessage={sendSocketMessage}
          isSocketConnected={isSocketConnected}
          modelSelection={modelSelection}
        />
      </div>
    </div>
  );
};

export default ChatApp;
