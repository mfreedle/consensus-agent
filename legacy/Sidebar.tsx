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
      {/* Mobile Overlay */}
      <div
        className={`mobile-overlay ${isOpen ? "active" : ""}`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <nav
        className={`
          layout-sidebar sidebar-content
          ${isOpen ? "mobile-open" : ""}
        `}
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Compact Header */}
        <div className="p-3 border-b border-primary-teal/20 flex items-center justify-between">
          <h2 className="text-base font-semibold text-primary-cyan">
            Navigation
          </h2>
          <button
            onClick={onClose}
            className="btn btn-ghost btn-sm lg:hidden"
            aria-label="Close sidebar"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto">
          {/* Active Session Group */}
          <div className="border-b border-primary-teal/10">
            <button
              onClick={() => toggleGroup("activeSession")}
              className="w-full flex items-center justify-between px-3 py-2.5 text-primary-cyan hover:bg-primary-teal/5 transition-colors"
              aria-expanded={!collapsedGroups.activeSession}
              aria-controls="active-session-content"
              aria-label="Toggle active session section"
            >
              <div className="flex items-center">
                <Smartphone className="w-4 h-4 mr-2" />
                <span className="font-medium text-sm">Active Session</span>
              </div>
              {collapsedGroups.activeSession ? (
                <ChevronRight className="w-4 h-4" aria-hidden="true" />
              ) : (
                <ChevronDown className="w-4 h-4" aria-hidden="true" />
              )}
            </button>

            {!collapsedGroups.activeSession && (
              <div
                className="px-3 pb-3"
                id="active-session-content"
                role="region"
                aria-labelledby="active-session-heading"
              >
                {/* New Chat Button */}
                <button
                  onClick={handleNewChat}
                  className="btn btn-primary w-full mb-3 text-sm"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  New Chat
                </button>

                {/* Current Chat Sessions */}
                <div className="space-y-1.5">
                  {isLoading ? (
                    <div className="loading-skeleton h-8 rounded"></div>
                  ) : sessions.length === 0 ? (
                    <div className="text-center py-3">
                      <div className="text-gray-400 text-xs">No chats yet</div>
                      <div className="text-gray-500 text-xs mt-1">
                        Create your first chat
                      </div>
                    </div>
                  ) : (
                    sessions.slice(0, 5).map((session) => (
                      <button
                        key={session.id}
                        onClick={() => onSessionSelect(session.id.toString())}
                        className={`w-full text-left p-2 rounded-md transition-colors ${
                          currentSessionId === session.id.toString()
                            ? "bg-primary-teal/20 border border-primary-teal/30 text-primary-cyan"
                            : "hover:bg-primary-teal/10 text-gray-300"
                        }`}
                      >
                        <div className="text-xs font-medium truncate">
                          {session.title ||
                            `Chat ${session.id.toString().slice(0, 8)}`}
                        </div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {new Date(session.created_at).toLocaleDateString()}
                        </div>
                      </button>
                    ))
                  )}
                </div>

                {/* Model Selection Preview - Compact */}
                <div className="mt-3 pt-3 border-t border-primary-teal/10">
                  <div className="text-xs font-medium text-gray-300 mb-1">
                    Models ({modelSelection.selectedModels.length})
                  </div>
                  <div className="text-xs text-gray-500 truncate">
                    {modelSelection.selectedModels.length === 0
                      ? "None selected"
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

          {/* Content Management Group - Compact */}
          <div className="border-b border-primary-teal/10">
            <button
              onClick={() => toggleGroup("contentManagement")}
              className="w-full flex items-center justify-between px-3 py-2.5 text-primary-cyan hover:bg-primary-teal/5 transition-colors"
              aria-expanded={!collapsedGroups.contentManagement}
              aria-controls="content-management-content"
              aria-label="Toggle content management section"
            >
              <div className="flex items-center">
                <FolderOpen className="w-4 h-4 mr-2" />
                <span className="font-medium text-sm">Content</span>
              </div>
              {collapsedGroups.contentManagement ? (
                <ChevronRight className="w-4 h-4" aria-hidden="true" />
              ) : (
                <ChevronDown className="w-4 h-4" aria-hidden="true" />
              )}
            </button>

            {!collapsedGroups.contentManagement && (
              <div
                className="px-3 pb-3"
                id="content-management-content"
                role="region"
                aria-labelledby="content-management-heading"
              >
                {/* Compact Tab Navigation */}
                <div
                  className="grid grid-cols-3 gap-1 mb-3"
                  role="tablist"
                  aria-label="Content management tabs"
                >
                  <button
                    onClick={() => setActiveTab("files")}
                    className={`flex flex-col items-center px-2 py-2 text-xs rounded-md transition-colors ${
                      activeTab === "files"
                        ? "bg-primary-teal/20 text-primary-cyan"
                        : "text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10"
                    }`}
                    role="tab"
                    aria-selected={activeTab === "files"}
                    aria-controls="files-panel"
                    id="files-tab"
                  >
                    <File className="w-3 h-3 mb-1" aria-hidden="true" />
                    Files
                  </button>
                  <button
                    onClick={() => setActiveTab("google")}
                    className={`flex flex-col items-center px-2 py-2 text-xs rounded-md transition-colors ${
                      activeTab === "google"
                        ? "bg-primary-teal/20 text-primary-cyan"
                        : "text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10"
                    }`}
                    role="tab"
                    aria-selected={activeTab === "google"}
                    aria-controls="google-panel"
                    id="google-tab"
                  >
                    <Cloud className="w-3 h-3 mb-1" aria-hidden="true" />
                    Drive
                  </button>
                  <button
                    onClick={() => setActiveTab("approvals")}
                    className={`flex flex-col items-center px-2 py-2 text-xs rounded-md transition-colors ${
                      activeTab === "approvals"
                        ? "bg-primary-teal/20 text-primary-cyan"
                        : "text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10"
                    }`}
                    role="tab"
                    aria-selected={activeTab === "approvals"}
                    aria-controls="approvals-panel"
                    id="approvals-tab"
                  >
                    <CheckCircle className="w-3 h-3 mb-1" aria-hidden="true" />
                    Approvals
                  </button>
                </div>

                {/* Compact Content Panels */}
                {activeTab === "files" && (
                  <div
                    className="border-t border-primary-teal/10 pt-3"
                    role="tabpanel"
                    id="files-panel"
                    aria-labelledby="files-tab"
                  >
                    <FileUpload />
                    <div className="mt-3">
                      <FileList />
                    </div>
                  </div>
                )}

                {activeTab === "google" && (
                  <div
                    className="border-t border-primary-teal/10 pt-3"
                    role="tabpanel"
                    id="google-panel"
                    aria-labelledby="google-tab"
                  >
                    <GoogleDriveIntegration />
                  </div>
                )}

                {activeTab === "approvals" && (
                  <div
                    className="border-t border-primary-teal/10 pt-3"
                    role="tabpanel"
                    id="approvals-panel"
                    aria-labelledby="approvals-tab"
                  >
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

          {/* Configuration Group - Compact */}
          <div className="border-b border-primary-teal/10">
            <button
              onClick={() => toggleGroup("configuration")}
              className="w-full flex items-center justify-between px-3 py-2.5 text-primary-cyan hover:bg-primary-teal/5 transition-colors"
            >
              <div className="flex items-center">
                <Cog className="w-4 h-4 mr-2" />
                <span className="font-medium text-sm">Config</span>
              </div>
              {collapsedGroups.configuration ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>

            {!collapsedGroups.configuration && (
              <div className="px-3 pb-3">
                <div className="grid grid-cols-2 gap-1 mb-3">
                  <button
                    onClick={() => setActiveTab("models")}
                    className={`flex flex-col items-center px-2 py-2 text-xs rounded-md transition-colors ${
                      activeTab === "models"
                        ? "bg-primary-teal/20 text-primary-cyan"
                        : "text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10"
                    }`}
                  >
                    <Bot className="w-3 h-3 mb-1" />
                    Models
                  </button>
                  <button className="flex flex-col items-center px-2 py-2 text-xs rounded-md transition-colors text-gray-400 hover:text-primary-cyan hover:bg-primary-teal/10">
                    <Settings className="w-3 h-3 mb-1" />
                    Settings
                  </button>
                </div>

                {activeTab === "models" && (
                  <div className="border-t border-primary-teal/10 pt-3">
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
      </nav>
    </>
  );
};

export default Sidebar;
