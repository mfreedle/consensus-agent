import React, { useState, useEffect, useCallback } from "react";
import {
  Settings,
  Database,
  Eye,
  EyeOff,
  Save,
  Key,
  RefreshCw,
  X,
  Power,
  Trash2,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { enhancedApiService } from "../services/enhancedApi";
import { useErrorHandler } from "../hooks/useErrorHandler";
import LoadingIndicator from "./LoadingIndicator";

// Types
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
  has_api_key?: boolean;
  last_sync_at?: string;
  sync_error?: string;
}

interface LLMModel {
  id: string;
  provider: string;
  display_name: string;
  description?: string;
  is_active?: boolean;
  supports_streaming?: boolean;
  supports_function_calling?: boolean;
  supports_vision?: boolean;
  context_window?: number;
  capabilities?: Record<string, any>;
}

interface UnifiedProviderModelManagementProps {
  className?: string;
}

// Default provider configurations
const defaultProviders: ProviderConfig[] = [
  {
    provider: "openai",
    display_name: "OpenAI",
    api_base_url: "https://api.openai.com/v1",
    is_active: true,
    max_requests_per_minute: 60,
    max_tokens_per_request: 64000,
    has_api_key: false,
  },
  {
    provider: "grok",
    display_name: "Grok (xAI)",
    api_base_url: "https://api.x.ai/v1",
    is_active: true,
    max_requests_per_minute: 60,
    max_tokens_per_request: 64000,
    has_api_key: false,
  },
  {
    provider: "deepseek",
    display_name: "DeepSeek",
    api_base_url: "https://api.deepseek.com/v1",
    is_active: true,
    max_requests_per_minute: 60,
    max_tokens_per_request: 64000,
    has_api_key: false,
  },
  {
    provider: "anthropic",
    display_name: "Anthropic",
    api_base_url: "https://api.anthropic.com/v1",
    is_active: true,
    max_requests_per_minute: 60,
    max_tokens_per_request: 64000,
    has_api_key: false,
  },
];

const UnifiedProviderModelManagement: React.FC<
  UnifiedProviderModelManagementProps
> = ({ className = "" }) => {
  // State for providers
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [showApiKey, setShowApiKey] = useState<{ [key: string]: boolean }>({});
  const [formData, setFormData] = useState<{
    [key: string]: Partial<ProviderConfig>;
  }>({});

  // State for models
  const [models, setModels] = useState<LLMModel[]>([]);
  const [expandedProviders, setExpandedProviders] = useState<Set<string>>(
    new Set()
  );
  const [modelFilter, setModelFilter] = useState<"all" | "active" | "inactive">(
    "all"
  );

  // General state
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"providers" | "models">(
    "providers"
  );
  const { addError } = useErrorHandler();

  // Load providers
  const loadProviders = useCallback(async () => {
    try {
      const response = await enhancedApiService.request<ProviderConfig[]>(
        "/models/providers",
        { method: "GET" }
      );

      if (response) {
        setProviders(response);
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
    }
  }, [addError]);

  // Load models
  const loadModels = useCallback(async () => {
    try {
      const response = await enhancedApiService.request<LLMModel[]>("/models", {
        method: "GET",
      });

      if (response) {
        setModels(response);
      }
    } catch (error) {
      addError(error, "api", "Failed to load models");
    }
  }, [addError]);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await Promise.all([loadProviders(), loadModels()]);
      setIsLoading(false);
    };
    loadData();
  }, [loadProviders, loadModels]);

  // Provider management functions
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
      setEditingProvider(null);
    } else {
      const currentProvider = providers.find((p) => p.provider === providerKey);
      const defaultProvider = defaultProviders.find(
        (p) => p.provider === providerKey
      );

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

  // Model management functions
  const toggleModel = async (modelId: string, isActive: boolean) => {
    try {
      await enhancedApiService.request(
        `/models/admin/models/${modelId}/toggle`,
        {
          method: "PATCH",
          body: JSON.stringify({ model_id: modelId, is_active: isActive }),
        }
      );

      // Update local state
      setModels((prev) =>
        prev.map((model) =>
          model.id === modelId ? { ...model, is_active: isActive } : model
        )
      );
    } catch (error) {
      addError(error, "api", `Failed to toggle model ${modelId}`);
    }
  };

  const deleteModel = async (modelId: string) => {
    try {
      await enhancedApiService.request(`/models/admin/models/${modelId}`, {
        method: "DELETE",
      });

      // Update local state
      setModels((prev) => prev.filter((model) => model.id !== modelId));
    } catch (error) {
      addError(error, "api", `Failed to delete model ${modelId}`);
    }
  };

  // Utility functions
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

  const getProviderModels = (provider: string) => {
    return models.filter((model) => model.provider === provider);
  };

  const getFilteredModels = () => {
    switch (modelFilter) {
      case "active":
        return models.filter((model) => model.is_active !== false);
      case "inactive":
        return models.filter((model) => model.is_active === false);
      default:
        return models;
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
          message="Loading provider and model configurations..."
        />
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with tabs */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Settings className="w-6 h-6 text-gray-600 dark:text-gray-400" />
            <Database className="w-6 h-6 text-gray-600 dark:text-gray-400" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Provider & Model Management
          </h2>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab("providers")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === "providers"
                ? "bg-primary-teal text-white"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}
          >
            Providers
          </button>
          <button
            onClick={() => setActiveTab("models")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === "models"
                ? "bg-primary-teal text-white"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}
          >
            Models
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === "providers" && (
        <div className="space-y-6">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Configure AI provider settings including API keys, endpoints, and
            rate limits.
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
                              showApiKey[provider.provider]
                                ? "text"
                                : "password"
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
                            className="px-3 py-2 border border-l-0 border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-600 text-gray-500 dark:text-gray-400 rounded-r-md hover:bg-gray-100 dark:hover:bg-gray-500"
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
                        <input
                          type="url"
                          value={config.api_base_url || ""}
                          onChange={(e) =>
                            handleFormChange(
                              provider.provider,
                              "api_base_url",
                              e.target.value
                            )
                          }
                          placeholder="https://api.example.com/v1"
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                        />
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
                            value={config.max_tokens_per_request || 64000}
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

                      {/* Active Checkbox */}
                      <div>
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
                          className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
                        >
                          <X className="w-4 h-4" />
                          <span>Cancel</span>
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Status
                        </span>
                        <span
                          className={`text-sm font-medium ${
                            config.is_active
                              ? "text-green-600 dark:text-green-400"
                              : "text-red-600 dark:text-red-400"
                          }`}
                        >
                          {config.is_active ? "Active" : "Inactive"}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Models
                        </span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {getProviderModels(provider.provider).length}
                        </span>
                      </div>
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
      )}

      {activeTab === "models" && (
        <div className="space-y-6">
          {/* Filter bar */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Manage individual AI models and their availability.
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white text-sm"
              >
                <option value="all">All Models</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
              </select>
              <button
                onClick={loadModels}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {/* Models grouped by provider */}
          <div className="space-y-4">
            {allProviders.map((provider) => {
              const providerModels = getFilteredModels().filter(
                (model) => model.provider === provider.provider
              );
              const isExpanded = expandedProviders.has(provider.provider);

              if (providerModels.length === 0) return null;

              return (
                <div
                  key={provider.provider}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                >
                  {/* Provider header */}
                  <button
                    onClick={() => {
                      const newExpanded = new Set(expandedProviders);
                      if (isExpanded) {
                        newExpanded.delete(provider.provider);
                      } else {
                        newExpanded.add(provider.provider);
                      }
                      setExpandedProviders(newExpanded);
                    }}
                    className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">
                        {getProviderIcon(provider.provider)}
                      </span>
                      <div className="text-left">
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {provider.display_name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {providerModels.length} models
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {
                          providerModels.filter((m) => m.is_active !== false)
                            .length
                        }{" "}
                        active
                      </span>
                      {isExpanded ? (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </button>

                  {/* Models list */}
                  {isExpanded && (
                    <div className="border-t border-gray-200 dark:border-gray-700">
                      {providerModels.map((model) => (
                        <div
                          key={model.id}
                          className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                        >
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {model.display_name}
                              </h4>
                              <span
                                className={`px-2 py-1 text-xs rounded-full ${
                                  model.is_active !== false
                                    ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                                    : "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
                                }`}
                              >
                                {model.is_active !== false
                                  ? "Active"
                                  : "Inactive"}
                              </span>
                            </div>
                            {model.description && (
                              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                {model.description}
                              </p>
                            )}
                            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                              {model.supports_streaming && (
                                <span className="flex items-center space-x-1">
                                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                  <span>Streaming</span>
                                </span>
                              )}
                              {model.supports_function_calling && (
                                <span className="flex items-center space-x-1">
                                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                                  <span>Functions</span>
                                </span>
                              )}
                              {model.supports_vision && (
                                <span className="flex items-center space-x-1">
                                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                  <span>Vision</span>
                                </span>
                              )}
                              {model.context_window && (
                                <span>
                                  {model.context_window.toLocaleString()} tokens
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() =>
                                toggleModel(
                                  model.id,
                                  !(model.is_active !== false)
                                )
                              }
                              className={`p-2 rounded-md transition-colors ${
                                model.is_active !== false
                                  ? "text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                                  : "text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20"
                              }`}
                              title={
                                model.is_active !== false
                                  ? "Deactivate"
                                  : "Activate"
                              }
                            >
                              <Power className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => deleteModel(model.id)}
                              className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                              title="Delete model"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {getFilteredModels().length === 0 && (
            <div className="text-center py-8">
              <Database className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No models found
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                {modelFilter === "all"
                  ? "No models have been configured yet."
                  : `No ${modelFilter} models found.`}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UnifiedProviderModelManagement;
