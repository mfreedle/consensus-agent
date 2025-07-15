import React, { useState } from "react";
import {
  Settings,
  User as UserIcon,
  Database,
  Users,
  Shield,
  BarChart3,
  RefreshCw,
  FileText,
  ArrowLeft,
} from "lucide-react";
import ProviderManagement from "./ProviderManagement";
import FileList from "./FileList";

interface AdminPanelProps {
  className?: string;
  onBack?: () => void;
}

type AdminTab =
  | "profile"
  | "providers"
  | "models"
  | "users"
  | "analytics"
  | "system"
  | "knowledge";

const AdminPanel: React.FC<AdminPanelProps> = ({ className = "", onBack }) => {
  const [activeTab, setActiveTab] = useState<AdminTab>("knowledge");
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [showFileViewer, setShowFileViewer] = useState(false);

  // Handle file deletion - trigger refresh
  const handleFileDeleted = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  // Handle file selection for viewing
  const handleFileSelect = (file: any) => {
    setSelectedFile(file);
    setShowFileViewer(true);
  };

  // Handle file download
  const handleDownload = (file: any) => {
    try {
      const downloadUrl = `/api/files/${file.id}/download`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = file.filename;
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const tabs = [
    {
      id: "profile" as AdminTab,
      label: "Profile",
      icon: UserIcon,
      description: "Manage your account and change password",
    },
    {
      id: "providers" as AdminTab,
      label: "Providers",
      icon: Settings,
      description: "Manage AI provider configurations and API keys",
    },
    {
      id: "models" as AdminTab,
      label: "Models",
      icon: Database,
      description: "View and manage available AI models",
    },
    {
      id: "knowledge" as AdminTab,
      label: "Knowledge Base",
      icon: FileText,
      description: "Manage uploaded documents and knowledge base files",
    },
    {
      id: "users" as AdminTab,
      label: "Users",
      icon: Users,
      description: "User management and permissions",
    },
    {
      id: "analytics" as AdminTab,
      label: "Analytics",
      icon: BarChart3,
      description: "Usage statistics and performance metrics",
    },
    {
      id: "system" as AdminTab,
      label: "System",
      icon: Shield,
      description: "System settings and maintenance",
    },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "profile":
        return (
          <div className="space-y-4 max-w-md mx-auto mt-8">
            <h2 className="text-xl font-bold mb-1">Profile</h2>
            <p className="text-gray-400 text-sm mb-4">
              Update your account information and change your password.
            </p>
            <form className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 flex flex-col gap-4">
              <div>
                <label
                  className="block text-gray-300 text-sm mb-1"
                  htmlFor="current-password"
                >
                  Current Password
                </label>
                <input
                  type="password"
                  id="current-password"
                  className="w-full p-2 rounded bg-gray-900 border border-gray-700 text-gray-100"
                  placeholder="Current password"
                />
              </div>
              <div>
                <label
                  className="block text-gray-300 text-sm mb-1"
                  htmlFor="new-password"
                >
                  New Password
                </label>
                <input
                  type="password"
                  id="new-password"
                  className="w-full p-2 rounded bg-gray-900 border border-gray-700 text-gray-100"
                  placeholder="New password"
                />
              </div>
              <div>
                <label
                  className="block text-gray-300 text-sm mb-1"
                  htmlFor="confirm-password"
                >
                  Confirm New Password
                </label>
                <input
                  type="password"
                  id="confirm-password"
                  className="w-full p-2 rounded bg-gray-900 border border-gray-700 text-gray-100"
                  placeholder="Confirm new password"
                />
              </div>
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition-colors"
              >
                Change Password
              </button>
            </form>
          </div>
        );

      case "providers":
        return <ProviderManagement />;

      case "knowledge":
        return (
          <div className="h-full flex flex-col space-y-4 bg-gray-700/10 rounded-lg p-2">
            <div className="flex-shrink-0 flex items-center justify-between bg-gray-800/30 rounded-lg p-3">
              <div>
                <h2 className="text-xl font-bold mb-1 text-white">
                  Knowledge Base Management
                </h2>
                <p className="text-gray-400 text-sm">
                  Manage your uploaded documents and knowledge base files
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setRefreshTrigger((prev) => prev + 1)}
                  className="p-2 hover:bg-gray-700/50 rounded-lg transition-colors"
                  title="Refresh file list"
                >
                  <RefreshCw className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>

            <div className="flex-1 bg-gray-900/50 rounded-lg border border-gray-600 overflow-hidden flex flex-col min-h-0">
              <div
                className="flex-1 overflow-y-auto min-h-0"
                style={{ maxHeight: "calc(100vh - 400px)" }}
              >
                <div className="p-3">
                  <FileList
                    refreshTrigger={refreshTrigger}
                    onFileDelete={handleFileDeleted}
                    onFileSelect={handleFileSelect}
                    showPagination={false}
                  />
                </div>
              </div>
            </div>

            <div className="flex-shrink-0 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <h4 className="font-medium text-blue-400 mb-2 text-sm">
                💡 How to add files to your knowledge base:
              </h4>
              <ul className="text-xs text-gray-300 space-y-1">
                <li>
                  • Use the chat interface and click "Document upload" button
                </li>
                <li>• Use the sidebar: Content Management → Files</li>
                <li>
                  • Files uploaded here are permanently stored and can be
                  referenced in any conversation
                </li>
              </ul>
            </div>
          </div>
        );

      case "models":
        return (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold mb-1">Model Management</h2>
              <p className="text-gray-400 text-sm">
                View and manage available AI models
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 text-center">
              <Database className="w-10 h-10 mx-auto mb-3 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">Model Management</h3>
              <p className="text-gray-400 mb-3 text-sm">
                Advanced model management features coming soon.
              </p>
              <p className="text-xs text-gray-500">
                The app now uses a curated list of hardcoded models. New models
                can be added manually through the admin interface.
              </p>
            </div>
          </div>
        );

      case "users":
        return (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold mb-1">User Management</h2>
              <p className="text-gray-400 text-sm">
                Manage users and permissions
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 text-center">
              <Users className="w-10 h-10 mx-auto mb-3 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">User Management</h3>
              <p className="text-gray-400 mb-3 text-sm">
                User management features coming soon.
              </p>
              <p className="text-xs text-gray-500">
                Currently supporting single-user mode.
              </p>
            </div>
          </div>
        );

      case "analytics":
        return (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold mb-1">Analytics & Usage</h2>
              <p className="text-gray-400 text-sm">
                View usage statistics and performance metrics
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 text-center">
              <BarChart3 className="w-10 h-10 mx-auto mb-3 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">
                Analytics Dashboard
              </h3>
              <p className="text-gray-400 mb-3 text-sm">
                Usage analytics and performance metrics coming soon.
              </p>
              <p className="text-xs text-gray-500">
                Track API usage, model performance, and system metrics.
              </p>
            </div>
          </div>
        );

      case "system":
        return (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold mb-1">System Settings</h2>
              <p className="text-gray-400 text-sm">
                System configuration and maintenance
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-lg border border-gray-700 p-6 text-center">
              <Shield className="w-10 h-10 mx-auto mb-3 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">
                System Configuration
              </h3>
              <p className="text-gray-400 mb-3 text-sm">
                System settings and maintenance tools coming soon.
              </p>
              <p className="text-xs text-gray-500">
                Database management, backup/restore, and system health
                monitoring.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-700 bg-gray-800/50 px-6 py-4">
        <div className="flex items-center gap-3">
          {onBack && (
            <button
              onClick={onBack}
              className="p-2 hover:bg-gray-700/50 rounded-lg transition-colors"
              aria-label="Back to chat"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </button>
          )}
          <Shield className="w-6 h-6 text-blue-400" />
          <div>
            <h1 className="text-xl font-bold">Admin Panel</h1>
            <p className="text-sm text-gray-400">
              System administration and configuration
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Compact Sidebar - Uniform Width */}
        <div className="flex-shrink-0 border-r border-gray-700 bg-gray-800/30 p-4 min-w-max">
          <nav className="flex flex-col space-y-4">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full text-left px-4 py-4 rounded-lg transition-all duration-200 whitespace-nowrap ${
                  activeTab === tab.id
                    ? "bg-blue-600/30 text-blue-300 border-2 border-blue-500/50 shadow-lg shadow-blue-500/20"
                    : "hover:bg-gray-700/50 text-gray-100 border-2 border-transparent hover:border-gray-600/30"
                }`}
                title={tab.description}
              >
                <div className="flex items-center gap-2.5">
                  <tab.icon
                    className={`w-4 h-4 flex-shrink-0 ${
                      activeTab === tab.id ? "text-blue-400" : "text-gray-300"
                    }`}
                  />
                  <span
                    className={`font-medium text-sm ${
                      activeTab === tab.id ? "text-blue-200" : "text-gray-100"
                    }`}
                  >
                    {tab.label}
                  </span>
                </div>
              </button>
            ))}
          </nav>

          {/* System Status with Text */}
          <div className="mt-6 p-3 bg-gray-700/30 rounded-lg border border-gray-600">
            <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
              <RefreshCw className="w-4 h-4" />
              <span className="font-medium">Status</span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Backend:</span>
                <span className="text-green-400 font-medium">Online</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Database:</span>
                <span className="text-green-400 font-medium">Connected</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Models:</span>
                <span className="text-yellow-400 font-medium">Checking...</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content - Maximum Space with Enhanced Layout */}
        <div className="flex-1 overflow-hidden bg-gray-800/20">
          <div className="p-4 h-full overflow-y-auto">{renderTabContent()}</div>
        </div>
      </div>

      {/* File Viewer Modal */}
      {showFileViewer && selectedFile && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg border border-gray-600 max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-600">
              <h3 className="text-lg font-semibold text-white">
                {selectedFile.filename}
              </h3>
              <button
                onClick={() => setShowFileViewer(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Size:</span>
                    <span className="ml-2 text-white">{selectedFile.size ? `${Math.round(selectedFile.size / 1024)} KB` : 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <span className="ml-2 text-white">{selectedFile.filename.split('.').pop()?.toUpperCase() || 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Uploaded:</span>
                    <span className="ml-2 text-white">{new Date(selectedFile.created_at).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Status:</span>
                    <span className="ml-2 text-green-400">Available</span>
                  </div>
                </div>
                <div className="pt-4 border-t border-gray-600">
                  <p className="text-gray-400 text-sm">
                    This file is available in your knowledge base and can be referenced by AI agents during conversations.
                  </p>
                </div>
              </div>
            </div>
            <div className="flex justify-end space-x-3 p-4 border-t border-gray-600">
              <button
                onClick={() => handleDownload(selectedFile)}
                className="px-4 py-2 bg-primary-teal text-white rounded-lg hover:bg-primary-teal/80 transition-colors"
              >
                Download
              </button>
              <button
                onClick={() => setShowFileViewer(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
