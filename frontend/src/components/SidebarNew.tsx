import React, { useState, useEffect } from "react";
import {
  X,
  Plus,
  Settings,
  File,
  Bot,
  Cloud,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Smartphone,
  FolderOpen,
  Cog,
} from "lucide-react";
import { apiService, ChatSession } from "../services/api";
import { ModelSelectionState } from "../types";
import FileUpload from "./FileUpload";
import FileList from "./FileList";
import ModelSelection from "./ModelSelection";
import { GoogleDriveIntegration } from "./GoogleDriveIntegration";
import { ApprovalDashboard } from "./ApprovalDashboard";
import { ApprovalViewer } from "./ApprovalViewer";
import { approvalService, DocumentApproval } from "../services/approvalService";

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
    "files" | "google" | "approvals" | "models"
  >("files");
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedApproval, setSelectedApproval] = useState<any>(null);
  const [showApprovalViewer, setShowApprovalViewer] = useState(false);

  // Collapsible group states
  const [collapsedGroups, setCollapsedGroups] = useState({
    activeSession: false,
    contentManagement: false,
    configuration: false,
  });

  const toggleGroup = (groupName: keyof typeof collapsedGroups) => {
    setCollapsedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }));
  };

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
      }
    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
  };

  const handleSelectApproval = (approval: DocumentApproval) => {
    setSelectedApproval(approval);
    setShowApprovalViewer(true);
  };

  const handleBackToDashboard = () => {
    setShowApprovalViewer(false);
    setSelectedApproval(null);
  };

  const handleApprovalChange = (updatedApproval: DocumentApproval) => {
    setSelectedApproval(updatedApproval);
  };

  const handleCreateTestApproval = async () => {
    try {
      const filesResult = await apiService.getUserFiles();
      if (filesResult.data && filesResult.data.files.length > 0) {
        const firstFile = filesResult.data.files[0];

        await approvalService.createApproval({
          file_id: firstFile.id,
          title: "Test Document Update",
          description:
            "This is a test approval request to demonstrate the workflow",
          change_type: "content_edit",
          original_content: "Original content...",
          proposed_content: "Updated content with test changes...",
          ai_reasoning:
            "This change improves clarity and adds important information",
          confidence_score: 85,
          expires_in_hours: 24,
        });

        setActiveTab("approvals");
      } else {
        console.error("No files available to create approval for");
      }
    } catch (error) {
      console.error("Failed to create test approval:", error);
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

        {/* Content - New Grouped Navigation */}
        <div className="flex-1 overflow-y-auto">
          {/* Active Session Group */}
          <div className="border-b border-primary-teal/10">
            <button
              onClick={() => toggleGroup("activeSession")}
              className="w-full flex items-center justify-between px-4 py-3 text-primary-cyan hover:bg-primary-teal/5 transition-colors"
            >
              <div className="flex items-center">
                <Smartphone className="w-4 h-4 mr-2" />
                <span className="font-medium">Active Session</span>
              </div>
              {collapsedGroups.activeSession ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>

            {!collapsedGroups.activeSession && (
              <div className="px-4 pb-4">
                {/* New Chat Button */}
                <button
                  onClick={handleNewChat}
                  className="w-full btn-gradient-primary font-medium py-3 px-4 rounded-lg hover:glow-effect-sm transition-all duration-200 mb-4 flex items-center justify-center"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  New Chat
                </button>

                {/* Current Chat Sessions */}
                <div className="space-y-2">
                  {isLoading ? (
                    <div className="text-gray-400 text-sm">
                      Loading chats...
                    </div>
                  ) : sessions.length === 0 ? (
                    <div className="text-center py-4">
                      <div className="text-gray-400 text-sm">No chats yet</div>
                      <div className="text-gray-500 text-xs mt-1">
                        Create your first chat to get started
                      </div>
                    </div>
                  ) : (
                    sessions.map((session) => (
                      <button
                        key={session.id}
                        onClick={() => onSessionSelect(session.id.toString())}
                        className={`w-full text-left p-3 rounded-lg transition-colors ${
                          currentSessionId === session.id.toString()
                            ? "bg-primary-teal/20 border border-primary-teal/30 text-primary-cyan"
                            : "hover:bg-primary-teal/10 text-gray-300"
                        }`}
                      >
                        <div className="text-sm font-medium truncate">
                          {session.title ||
                            `Chat ${session.id.toString().slice(0, 8)}`}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {new Date(session.created_at).toLocaleDateString()}
                        </div>
                      </button>
                    ))
                  )}
                </div>

                {/* Model Selection Preview */}
                <div className="mt-4 pt-4 border-t border-primary-teal/10">
                  <div className="text-sm font-medium text-gray-300 mb-2">
                    Model Selection ({modelSelection.selectedModels.length}{" "}
                    selected)
                  </div>
                  <div className="text-xs text-gray-500">
                    {modelSelection.selectedModels.length === 0
                      ? "No models selected"
                      : `${modelSelection.selectedModels
                          .slice(0, 2)
                          .join(", ")}${
                          modelSelection.selectedModels.length > 2 ? "..." : ""
                        }`}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Content Management Group */}
          <div className="border-b border-primary-teal/10">
            <button
              onClick={() => toggleGroup("contentManagement")}
              className="w-full flex items-center justify-between px-4 py-3 text-primary-cyan hover:bg-primary-teal/5 transition-colors"
            >
              <div className="flex items-center">
                <FolderOpen className="w-4 h-4 mr-2" />
                <span className="font-medium">Content Management</span>
              </div>
              {collapsedGroups.contentManagement ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>

            {!collapsedGroups.contentManagement && (
              <div className="px-4 pb-4">
                {/* Sub-navigation for content */}
                <div className="space-y-1 mb-4">
                  <button
                    onClick={() => setActiveTab("files")}
                    className={`w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                      activeTab === "files"
                        ? "bg-primary-teal/20 text-primary-cyan"
                        : "text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10"
                    }`}
                  >
                    <File className="w-4 h-4 mr-2" />
                    Knowledge Base
                  </button>
                  <button
                    onClick={() => setActiveTab("google")}
                    className={`w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                      activeTab === "google"
                        ? "bg-primary-teal/20 text-primary-cyan"
                        : "text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10"
                    }`}
                  >
                    <Cloud className="w-4 h-4 mr-2" />
                    Google Drive
                  </button>
                  <button
                    onClick={() => setActiveTab("approvals")}
                    className={`w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                      activeTab === "approvals"
                        ? "bg-primary-teal/20 text-primary-cyan"
                        : "text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10"
                    }`}
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Approvals
                  </button>
                </div>

                {/* Content based on active sub-tab */}
                {activeTab === "files" && (
                  <div className="border-t border-primary-teal/10 pt-4">
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-primary-cyan mb-1">
                        Knowledge Base Files
                      </h4>
                      <p className="text-xs text-gray-500">
                        Upload files to your permanent knowledge base
                      </p>
                    </div>
                    <FileUpload />
                    <div className="mt-4">
                      <FileList />
                    </div>
                  </div>
                )}

                {activeTab === "google" && (
                  <div className="border-t border-primary-teal/10 pt-4">
                    <GoogleDriveIntegration />
                  </div>
                )}

                {activeTab === "approvals" && (
                  <div className="border-t border-primary-teal/10 pt-4">
                    {showApprovalViewer && selectedApproval ? (
                      <ApprovalViewer
                        approval={selectedApproval}
                        onBack={handleBackToDashboard}
                        onApprovalChange={handleApprovalChange}
                      />
                    ) : (
                      <ApprovalDashboard
                        onCreateApproval={handleCreateTestApproval}
                        onSelectApproval={handleSelectApproval}
                      />
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Configuration Group */}
          <div className="border-b border-primary-teal/10">
            <button
              onClick={() => toggleGroup("configuration")}
              className="w-full flex items-center justify-between px-4 py-3 text-primary-cyan hover:bg-primary-teal/5 transition-colors"
            >
              <div className="flex items-center">
                <Cog className="w-4 h-4 mr-2" />
                <span className="font-medium">Configuration</span>
              </div>
              {collapsedGroups.configuration ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>

            {!collapsedGroups.configuration && (
              <div className="px-4 pb-4">
                <div className="space-y-1 mb-4">
                  <button
                    onClick={() => setActiveTab("models")}
                    className={`w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                      activeTab === "models"
                        ? "bg-primary-teal/20 text-primary-cyan"
                        : "text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10"
                    }`}
                  >
                    <Bot className="w-4 h-4 mr-2" />
                    AI Models
                  </button>
                  <button className="w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10">
                    <Settings className="w-4 h-4 mr-2" />
                    Settings
                  </button>
                </div>

                {activeTab === "models" && (
                  <div className="border-t border-primary-teal/10 pt-4">
                    <ModelSelection
                      selectedModels={modelSelection.selectedModels}
                      debateMode={modelSelection.debateMode}
                      showDebateProcess={modelSelection.showDebateProcess}
                      onModelSelectionChange={onModelSelectionChange}
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
export {};
