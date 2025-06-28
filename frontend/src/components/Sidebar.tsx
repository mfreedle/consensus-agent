import React, { useState, useEffect } from "react";
import {
  X,
  Plus,
  MessageSquare,
  Settings,
  File,
  Bot,
  Cloud,
  CheckCircle,
} from "lucide-react";
import { apiService, ChatSession } from "../services/api";
import { ModelSelectionState } from "../types";
import FileUpload from "./FileUpload";
import FileList from "./FileList";
import ModelSelection from "./ModelSelection";
import { GoogleDriveIntegration } from "./GoogleDriveIntegration";
import { ApprovalDashboard } from "./ApprovalDashboard";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  modelSelection?: ModelSelectionState;
  onModelSelectionChange?: (selection: ModelSelectionState) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  currentSessionId,
  onSessionSelect,
  modelSelection = {
    selectedModels: [],
    debateMode: "consensus",
    showDebateProcess: true,
  },
  onModelSelectionChange = () => {},
}) => {
  const [activeTab, setActiveTab] = useState<
    "chats" | "files" | "models" | "google" | "approvals"
  >("chats");
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [fileRefreshTrigger, setFileRefreshTrigger] = useState(0);

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

  // File upload handlers
  const handleFileUploadSuccess = (file: any) => {
    console.log("File uploaded successfully:", file);
    // Trigger file list refresh
    setFileRefreshTrigger((prev) => prev + 1);
  };

  const handleFileUploadError = (error: string) => {
    console.error("File upload error:", error);
    // TODO: Show error toast to user
  };

  const handleFileDelete = (file: any) => {
    console.log("File deleted:", file);
    // Trigger file list refresh
    setFileRefreshTrigger((prev) => prev + 1);
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
        fixed lg:relative inset-y-0 left-0 z-50 w-80 sm:w-96 lg:w-80 bg-bg-dark-secondary border-r border-primary-teal/20 transform transition-transform duration-300 ease-in-out flex flex-col
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
        <div className="flex border-b border-primary-teal/20 overflow-x-auto">
          <button
            onClick={() => setActiveTab("chats")}
            className={`flex-shrink-0 px-2 sm:px-3 py-3 text-xs sm:text-sm font-medium transition-colors min-w-0 ${
              activeTab === "chats"
                ? "text-primary-cyan border-b-2 border-primary-cyan"
                : "text-gray-400 hover:text-primary-cyan"
            }`}
          >
            <MessageSquare className="w-3 h-3 sm:w-4 sm:h-4 inline-block mr-1" />
            <span className="hidden xs:inline">Chats</span>
          </button>
          <button
            onClick={() => setActiveTab("files")}
            className={`flex-shrink-0 px-2 sm:px-3 py-3 text-xs sm:text-sm font-medium transition-colors min-w-0 ${
              activeTab === "files"
                ? "text-primary-cyan border-b-2 border-primary-cyan"
                : "text-gray-400 hover:text-primary-cyan"
            }`}
          >
            <File className="w-3 h-3 sm:w-4 sm:h-4 inline-block mr-1" />
            <span className="hidden xs:inline">Files</span>
          </button>
          <button
            onClick={() => setActiveTab("google")}
            className={`flex-shrink-0 px-2 sm:px-3 py-3 text-xs sm:text-sm font-medium transition-colors min-w-0 ${
              activeTab === "google"
                ? "text-primary-cyan border-b-2 border-primary-cyan"
                : "text-gray-400 hover:text-primary-cyan"
            }`}
          >
            <Cloud className="w-3 h-3 sm:w-4 sm:h-4 inline-block mr-1" />
            <span className="hidden xs:inline">Drive</span>
          </button>
          <button
            onClick={() => setActiveTab("models")}
            className={`flex-shrink-0 px-2 sm:px-3 py-3 text-xs sm:text-sm font-medium transition-colors min-w-0 ${
              activeTab === "models"
                ? "text-primary-cyan border-b-2 border-primary-cyan"
                : "text-gray-400 hover:text-primary-cyan"
            }`}
          >
            <Bot className="w-3 h-3 sm:w-4 sm:h-4 inline-block mr-1" />
            <span className="hidden xs:inline">Models</span>
          </button>
          <button
            onClick={() => setActiveTab("approvals")}
            className={`flex-shrink-0 px-2 sm:px-3 py-3 text-xs sm:text-sm font-medium transition-colors min-w-0 ${
              activeTab === "approvals"
                ? "text-primary-cyan border-b-2 border-primary-cyan"
                : "text-gray-400 hover:text-primary-cyan"
            }`}
          >
            <CheckCircle className="w-3 h-3 sm:w-4 sm:h-4 inline-block mr-1" />
            <span className="hidden xs:inline">Approvals</span>
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
          )}{" "}
          {activeTab === "files" && (
            <div className="p-4">
              {/* File Upload Section */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-primary-cyan mb-3">
                  Upload Files
                </h3>
                <FileUpload
                  onUploadSuccess={handleFileUploadSuccess}
                  onUploadError={handleFileUploadError}
                  maxFiles={5}
                  className="mb-4"
                />
              </div>

              {/* File List Section */}
              <div>
                <h3 className="text-sm font-medium text-primary-cyan mb-3">
                  Your Files
                </h3>
                <FileList
                  onFileDelete={handleFileDelete}
                  refreshTrigger={fileRefreshTrigger}
                  className="max-h-96 overflow-y-auto"
                />
              </div>
            </div>
          )}
          {activeTab === "google" && (
            <div className="p-4">
              <GoogleDriveIntegration />
            </div>
          )}
          {activeTab === "models" && (
            <ModelSelection
              selectedModels={modelSelection.selectedModels}
              debateMode={modelSelection.debateMode}
              showDebateProcess={modelSelection.showDebateProcess}
              onModelSelectionChange={onModelSelectionChange}
            />
          )}
          {activeTab === "approvals" && (
            <div className="p-4">
              <ApprovalDashboard />
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
