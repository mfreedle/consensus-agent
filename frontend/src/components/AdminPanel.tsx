import React, { useState } from "react";
import {
  Settings,
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
  | "providers"
  | "models"
  | "users"
  | "analytics"
  | "system"
  | "knowledge";

const AdminPanel: React.FC<AdminPanelProps> = ({ className = "", onBack }) => {
  const [activeTab, setActiveTab] = useState<AdminTab>("knowledge");

  const tabs = [
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
      case "providers":
        return <ProviderManagement />;

      case "knowledge":
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Knowledge Base</h2>
              <p className="text-gray-400">
                Manage your uploaded documents and knowledge base files
              </p>
            </div>

            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-6 h-6 text-blue-400" />
                <div>
                  <h3 className="text-lg font-semibold">Document Library</h3>
                  <p className="text-sm text-gray-400">
                    View and manage all documents in your knowledge base
                  </p>
                </div>
              </div>

              <div className="bg-gray-900/50 rounded-lg border border-gray-600 p-4">
                <FileList className="max-h-96 overflow-y-auto" />
              </div>

              <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <h4 className="font-medium text-blue-400 mb-2">
                  💡 How to add files to your knowledge base:
                </h4>
                <ul className="text-sm text-gray-300 space-y-1">
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
          </div>
        );

      case "models":
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Model Management</h2>
              <p className="text-gray-400">
                View and manage available AI models
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-8 text-center">
              <Database className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">Model Management</h3>
              <p className="text-gray-400 mb-4">
                Advanced model management features coming soon.
              </p>
              <p className="text-sm text-gray-500">
                For now, use the Providers tab to sync models from your
                configured providers.
              </p>
            </div>
          </div>
        );

      case "users":
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">User Management</h2>
              <p className="text-gray-400">Manage users and permissions</p>
            </div>
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-8 text-center">
              <Users className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">User Management</h3>
              <p className="text-gray-400 mb-4">
                User management features coming soon.
              </p>
              <p className="text-sm text-gray-500">
                Currently supporting single-user mode.
              </p>
            </div>
          </div>
        );

      case "analytics":
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Analytics & Usage</h2>
              <p className="text-gray-400">
                View usage statistics and performance metrics
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-8 text-center">
              <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">
                Analytics Dashboard
              </h3>
              <p className="text-gray-400 mb-4">
                Usage analytics and performance metrics coming soon.
              </p>
              <p className="text-sm text-gray-500">
                Track API usage, model performance, and system metrics.
              </p>
            </div>
          </div>
        );

      case "system":
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">System Settings</h2>
              <p className="text-gray-400">
                System configuration and maintenance
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-8 text-center">
              <Shield className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">
                System Configuration
              </h3>
              <p className="text-gray-400 mb-4">
                System settings and maintenance tools coming soon.
              </p>
              <p className="text-sm text-gray-500">
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
        {/* Sidebar */}
        <div className="w-64 border-r border-gray-700 bg-gray-800/30 p-4">
          <nav className="space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "hover:bg-gray-700/50 text-gray-300"
                }`}
              >
                <div className="flex items-center gap-3">
                  <tab.icon className="w-5 h-5" />
                  <div>
                    <div className="font-medium">{tab.label}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {tab.description}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </nav>

          <div className="mt-8 p-3 bg-gray-700/30 rounded-lg border border-gray-600">
            <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
              <RefreshCw className="w-4 h-4" />
              System Status
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span>Backend:</span>
                <span className="text-green-400">Online</span>
              </div>
              <div className="flex justify-between">
                <span>Database:</span>
                <span className="text-green-400">Connected</span>
              </div>
              <div className="flex justify-between">
                <span>Models:</span>
                <span className="text-yellow-400">Checking...</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">{renderTabContent()}</div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
