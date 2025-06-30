import React, { useState, useEffect, useCallback } from "react";
import {
  Settings,
  Eye,
  EyeOff,
  Save,
  RotateCw,
  Key,
  Globe,
} from "lucide-react";
import { enhancedApiService } from "../services/enhancedApi";
import { useErrorHandler } from "../hooks/useErrorHandler";
import LoadingIndicator from "./LoadingIndicator";

interface ProviderConfig {
  id?: number;
  provider: string;
  display_name: string;
  api_key?: string;
  api_base_url?: string;
  organization_id?: string;
  is_active: boolean;
  max_requests_per_minute: number;
  max_tokens_per_request: number;
  auto_sync_models: boolean;
  has_api_key?: boolean;
  last_sync_at?: string;
  sync_error?: string;
}

interface ProviderManagementProps {
  className?: string;
}

const defaultProviders: ProviderConfig[] = [
  {
    provider: "openai",
    display_name: "OpenAI",
    api_base_url: "https://api.openai.com/v1",
    is_active: true,
    max_requests_per_minute: 60,
    max_tokens_per_request: 4000,
    auto_sync_models: true,
    has_api_key: false,
  },
  {
    provider: "grok",
    display_name: "Grok (xAI)",
    api_base_url: "https://api.x.ai/v1",
    is_active: true,
    max_requests_per_minute: 60,
    max_tokens_per_request: 4000,
    auto_sync_models: true,
    has_api_key: false,
  },
  {
    provider: "deepseek",
    display_name: "DeepSeek",
    api_base_url: "https://api.deepseek.com/v1",
    is_active: true,
    max_requests_per_minute: 60,
    max_tokens_per_request: 4000,
    auto_sync_models: true,
    has_api_key: false,
  },
  {
    provider: "anthropic",
    display_name: "Anthropic",
    api_base_url: "https://api.anthropic.com/v1",
    is_active: true,
    max_requests_per_minute: 60,
    max_tokens_per_request: 4000,
    auto_sync_models: true,
    has_api_key: false,
  },
];

const ProviderManagement: React.FC<ProviderManagementProps> = ({
  className = "",
}) => {
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [showApiKey, setShowApiKey] = useState<{ [key: string]: boolean }>({});
  const [formData, setFormData] = useState<{
    [key: string]: Partial<ProviderConfig>;
  }>({});
  const { addError } = useErrorHandler();

  const loadProviders = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await enhancedApiService.request<ProviderConfig[]>(
        "/models/providers",
        { method: "GET" }
      );

      if (response) {
        setProviders(response);

        // Initialize form data for existing providers
        const initialFormData: { [key: string]: Partial<ProviderConfig> } = {};
        response.forEach((provider) => {
          initialFormData[provider.provider] = { ...provider };
        });

        // Add default providers if they don't exist
        defaultProviders.forEach((defaultProvider) => {
          if (!response.some((p) => p.provider === defaultProvider.provider)) {
            initialFormData[defaultProvider.provider] = defaultProvider;
          }
        });

        setFormData(initialFormData);
      } else {
        // If no providers exist, use defaults
        setProviders([]);
        const initialFormData: { [key: string]: Partial<ProviderConfig> } = {};
        defaultProviders.forEach((provider) => {
          initialFormData[provider.provider] = provider;
        });
        setFormData(initialFormData);
      }
    } catch (error) {
      addError(error, "api", "Failed to load provider configurations");
    } finally {
      setIsLoading(false);
    }
  }, [addError]);

  useEffect(() => {
    loadProviders();
  }, [loadProviders]);

  const handleSaveProvider = async (providerKey: string) => {
    const config = formData[providerKey];
    if (!config) return;

    try {
      const response = await enhancedApiService.request("/models/providers", {
        method: "POST",
        body: JSON.stringify(config),
      });

      if (response) {
        setEditingProvider(null);
        await loadProviders();
      }
    } catch (error) {
      addError(
        error,
        "api",
        `Failed to save provider '${config.display_name}'`
      );
    }
  };

  const handleSyncModels = async () => {
    setIsSyncing(true);
    try {
      const response = await enhancedApiService.request<{
        message: string;
        created: number;
        updated: number;
        providers: string[];
      }>("/models/sync", {
        method: "POST",
      });

      if (response) {
        await loadProviders();
      }
    } catch (error) {
      addError(error, "api", "Failed to sync models");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleFormChange = (
    providerKey: string,
    field: keyof ProviderConfig,
    value: any
  ) => {
    setFormData((prev) => ({
      ...prev,
      [providerKey]: {
        ...prev[providerKey],
        [field]: value,
      },
    }));
  };

  const toggleApiKeyVisibility = (providerKey: string) => {
    setShowApiKey((prev) => ({
      ...prev,
      [providerKey]: !prev[providerKey],
    }));
  };

  const handleEditProvider = (providerKey: string) => {
    if (editingProvider === providerKey) {
      // Stop editing
      setEditingProvider(null);
    } else {
      // Start editing - ensure form data is properly initialized
      const currentProvider = providers.find((p) => p.provider === providerKey);
      const defaultProvider = defaultProviders.find(
        (p) => p.provider === providerKey
      );

      // Initialize form data with current provider data or default
      const initData = currentProvider || defaultProvider;
      if (initData) {
        setFormData((prev) => ({
          ...prev,
          [providerKey]: { ...initData },
        }));
      }

      setEditingProvider(providerKey);
    }
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case "openai":
        return "🤖";
      case "grok":
        return "⚡";
      case "deepseek":
        return "🔍";
      case "anthropic":
        return "🎭";
      default:
        return "🔧";
    }
  };

  const allProviders = [
    ...providers,
    ...defaultProviders.filter(
      (defaultProvider) =>
        !providers.some((p) => p.provider === defaultProvider.provider)
    ),
  ];

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <LoadingIndicator
          isLoading={true}
          size="lg"
          message="Loading provider configurations..."
        />
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Settings className="w-6 h-6 text-gray-600 dark:text-gray-400" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Provider Management
          </h2>
        </div>
        <button
          onClick={handleSyncModels}
          disabled={isSyncing}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
        >
          <RotateCw className={`w-4 h-4 ${isSyncing ? "animate-spin" : ""}`} />
          <span>{isSyncing ? "Syncing..." : "Sync Models"}</span>
        </button>
      </div>

      {/* Provider Cards */}
      <div className="grid gap-6 md:grid-cols-2">
        {allProviders.map((provider) => {
          const isEditing = editingProvider === provider.provider;
          const config = formData[provider.provider] || provider;

          return (
            <div
              key={provider.provider}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
            >
              {/* Provider Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">
                    {getProviderIcon(provider.provider)}
                  </span>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {config.display_name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {provider.provider}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {provider.has_api_key && (
                    <div className="flex items-center text-green-600 dark:text-green-400">
                      <Key className="w-4 h-4" />
                    </div>
                  )}
                  <button
                    onClick={() => handleEditProvider(provider.provider)}
                    className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {isEditing ? (
                <div className="space-y-4">
                  {/* API Key */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      API Key
                    </label>
                    <div className="flex">
                      <input
                        type={
                          showApiKey[provider.provider] ? "text" : "password"
                        }
                        value={config.api_key || ""}
                        onChange={(e) =>
                          handleFormChange(
                            provider.provider,
                            "api_key",
                            e.target.value
                          )
                        }
                        placeholder="Enter API key..."
                        className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-l-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                      <button
                        type="button"
                        onClick={() =>
                          toggleApiKeyVisibility(provider.provider)
                        }
                        className="px-3 py-2 border border-l-0 border-gray-300 dark:border-gray-600 rounded-r-md bg-gray-50 dark:bg-gray-600 hover:bg-gray-100 dark:hover:bg-gray-500"
                      >
                        {showApiKey[provider.provider] ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* API Base URL */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      API Base URL
                    </label>
                    <div className="flex items-center">
                      <Globe className="w-4 h-4 text-gray-400 mr-2" />
                      <input
                        type="text"
                        value={config.api_base_url || ""}
                        onChange={(e) =>
                          handleFormChange(
                            provider.provider,
                            "api_base_url",
                            e.target.value
                          )
                        }
                        className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                  </div>

                  {/* Organization ID (for OpenAI) */}
                  {provider.provider === "openai" && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Organization ID (Optional)
                      </label>
                      <input
                        type="text"
                        value={config.organization_id || ""}
                        onChange={(e) =>
                          handleFormChange(
                            provider.provider,
                            "organization_id",
                            e.target.value
                          )
                        }
                        placeholder="org-..."
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                  )}

                  {/* Settings */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Max Requests/Min
                      </label>
                      <input
                        type="number"
                        value={config.max_requests_per_minute || 60}
                        onChange={(e) =>
                          handleFormChange(
                            provider.provider,
                            "max_requests_per_minute",
                            parseInt(e.target.value)
                          )
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Max Tokens
                      </label>
                      <input
                        type="number"
                        value={config.max_tokens_per_request || 4000}
                        onChange={(e) =>
                          handleFormChange(
                            provider.provider,
                            "max_tokens_per_request",
                            parseInt(e.target.value)
                          )
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                  </div>

                  {/* Toggles */}
                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={config.is_active || false}
                        onChange={(e) =>
                          handleFormChange(
                            provider.provider,
                            "is_active",
                            e.target.checked
                          )
                        }
                        className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        Provider Active
                      </span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={config.auto_sync_models || false}
                        onChange={(e) =>
                          handleFormChange(
                            provider.provider,
                            "auto_sync_models",
                            e.target.checked
                          )
                        }
                        className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        Auto-sync Models
                      </span>
                    </label>
                  </div>

                  {/* Actions */}
                  <div className="flex space-x-3 pt-4">
                    <button
                      onClick={() => handleSaveProvider(provider.provider)}
                      className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors"
                    >
                      <Save className="w-4 h-4" />
                      <span>Save</span>
                    </button>
                    <button
                      onClick={() => setEditingProvider(null)}
                      className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Status */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Status:
                    </span>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        config.is_active
                          ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                          : "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
                      }`}
                    >
                      {config.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>

                  {/* API Key Status */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      API Key:
                    </span>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        provider.has_api_key
                          ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                          : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                      }`}
                    >
                      {provider.has_api_key ? "Configured" : "Not Set"}
                    </span>
                  </div>

                  {/* Last Sync */}
                  {provider.last_sync_at && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Last Sync:
                      </span>
                      <span className="text-sm text-gray-900 dark:text-white">
                        {new Date(provider.last_sync_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}

                  {/* Sync Error */}
                  {provider.sync_error && (
                    <div className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded-md">
                      {provider.sync_error}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProviderManagement;
