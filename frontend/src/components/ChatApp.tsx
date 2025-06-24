import React, { useState } from "react";
import Header from "./Header";
import ChatInterface from "./ChatInterface";
import Sidebar from "./Sidebar";
import AuthModal from "./AuthModal";

const ChatApp: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  const handleLogin = (user: any) => {
    setIsAuthenticated(true);
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser(null);
    setCurrentSessionId(null);
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  if (!isAuthenticated) {
    return <AuthModal onLogin={handleLogin} />;
  }

  return (
    <div className="flex h-screen bg-bg-dark text-white">
      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        currentSessionId={currentSessionId}
        onSessionSelect={setCurrentSessionId}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {" "}
        {/* Header */}
        <Header
          onToggleSidebar={toggleSidebar}
          onLogout={handleLogout}
          currentUser={currentUser}
        />
        {/* Chat Interface */}
        <ChatInterface
          sessionId={currentSessionId}
          onSessionCreated={setCurrentSessionId}
        />
      </div>
    </div>
  );
};

export default ChatApp;
