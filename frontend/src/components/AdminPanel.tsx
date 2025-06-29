import React, { useState } from "react";
import {
  Settings,
  Database,
  Users,
  Shield,
  BarChart3,
  RefreshCw,
} from "lucide-react";
import ProviderManagement from "./ProviderManagement";

interface AdminPanelProps {
  className?: string;
}

type AdminTab = "providers" | "models" | "users" | "analytics" | "system";

const AdminPanel: React.FC<AdminPanelProps> = ({ className = "" }) => {
  const [activeTab, setActiveTab] = useState<AdminTab>("providers");

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
