import React, { useState, useEffect } from "react";
import { X, Plus, MessageSquare, Settings, File, Bot } from "lucide-react";
import { apiService, ChatSession } from "../services/api";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  currentSessionId,
  onSessionSelect,
}) => {
  const [activeTab, setActiveTab] = useState<"chats" | "files" | "models">(
    "chats"
  );
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && activeTab === "chats") {
      loadSessions();
    }
  }, [isOpen, activeTab]);

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
      }
    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
  };

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
        fixed lg:relative inset-y-0 left-0 z-50 w-80 bg-bg-dark-secondary border-r border-primary-teal/20 transform transition-transform duration-300 ease-in-out flex flex-col
        ${isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
      `}
      >
        {/* Header */}
        <div className="p-4 border-b border-primary-teal/20 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-primary-cyan">
            Navigation
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-primary-teal/10 transition-colors lg:hidden"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-primary-teal/20">
          <button
            onClick={() => setActiveTab("chats")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "chats"
                ? "text-primary-cyan border-b-2 border-primary-cyan"
                : "text-gray-400 hover:text-primary-cyan"
            }`}
          >
            <MessageSquare className="w-4 h-4 inline-block mr-2" />
            Chats
          </button>
          <button
            onClick={() => setActiveTab("files")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "files"
                ? "text-primary-cyan border-b-2 border-primary-cyan"
                : "text-gray-400 hover:text-primary-cyan"
            }`}
          >
            <File className="w-4 h-4 inline-block mr-2" />
            Files
          </button>
          <button
            onClick={() => setActiveTab("models")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "models"
                ? "text-primary-cyan border-b-2 border-primary-cyan"
                : "text-gray-400 hover:text-primary-cyan"
            }`}
          >
            <Bot className="w-4 h-4 inline-block mr-2" />
            Models
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === "chats" && (
            <div className="p-4">
              {/* New Chat Button */}
              <button
                onClick={handleNewChat}
                className="w-full btn-gradient-primary text-white font-medium py-3 px-4 rounded-lg hover:glow-effect-sm transition-all duration-200 mb-4 flex items-center justify-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Chat
              </button>{" "}
              {/* Chat Sessions */}
              <div className="space-y-2">
                {isLoading ? (
                  <div className="text-center py-4">
                    <div className="text-gray-400 text-sm">
                      Loading sessions...
                    </div>
                  </div>
                ) : sessions.length > 0 ? (
                  sessions.map((session) => (
                    <button
                      key={session.id}
                      onClick={() => onSessionSelect(session.id.toString())}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        currentSessionId === session.id.toString()
                          ? "bg-primary-teal/20 border border-primary-teal/30"
                          : "hover:bg-primary-teal/10"
                      }`}
                    >
                      <h3 className="font-medium text-white text-sm truncate mb-1">
                        {session.title}
                      </h3>
                      <p className="text-gray-500 text-xs">
                        {new Date(session.updated_at).toLocaleDateString()}
                      </p>
                    </button>
                  ))
                ) : (
                  <div className="text-center py-4">
                    <div className="text-gray-400 text-sm">No chats yet</div>
                    <div className="text-gray-500 text-xs mt-1">
                      Create your first chat to get started
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "files" && (
            <div className="p-4">
              <div className="text-center text-gray-400 py-8">
                <File className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p className="text-sm">No files uploaded yet</p>
                <button className="mt-2 text-primary-cyan text-sm hover:underline">
                  Upload a file
                </button>
              </div>
            </div>
          )}

          {activeTab === "models" && (
            <div className="p-4">
              <div className="space-y-3">
                <div className="p-3 bg-primary-teal/10 rounded-lg border border-primary-teal/20">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-primary-cyan">
                      OpenAI GPT-4
                    </h3>
                    <div className="w-2 h-2 bg-primary-green rounded-full"></div>
                  </div>
                  <p className="text-gray-400 text-xs">
                    Active • High reasoning
                  </p>
                </div>

                <div className="p-3 bg-primary-blue/10 rounded-lg border border-primary-blue/20">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-primary-azure">Grok-2</h3>
                    <div className="w-2 h-2 bg-primary-green rounded-full"></div>
                  </div>
                  <p className="text-gray-400 text-xs">
                    Active • Real-time insights
                  </p>
                </div>

                <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-300">Claude-3</h3>
                    <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                  </div>
                  <p className="text-gray-400 text-xs">
                    Inactive • Not configured
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-primary-teal/20">
          <button className="w-full flex items-center justify-center px-4 py-2 text-gray-400 hover:text-primary-cyan transition-colors">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
