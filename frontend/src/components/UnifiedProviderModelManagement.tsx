import React, { useState, useEffect, useCallback } from "react";
import {
  Settings,
  Database,
  Eye,
  EyeOff,
  Save,
  Key,
  RefreshCw,
  Power,
  Trash2,
  ChevronDown,
  ChevronRight,
  Plus,
  Globe,
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
  const [newModelForm, setNewModelForm] = useState<{
    [provider: string]: { modelId: string; displayName: string; show: boolean };
  }>({});
  const [addingNewProvider, setAddingNewProvider] = useState(false);
  const [newProviderForm, setNewProviderForm] = useState({
    provider: "",
    display_name: "",
    api_base_url: "",
  });

  // General state
  const [isLoading, setIsLoading] = useState(true);
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

  const allProviders = [
    ...providers,
    ...defaultProviders.filter(
      (defaultProvider) =>
        !providers.some((p) => p.provider === defaultProvider.provider)
    ),
  ];

  // Helper functions
  const getModelIdPlaceholder = (provider: string) => {
    switch (provider) {
      case "openai":
        return "e.g., gpt-4, gpt-4-turbo, gpt-3.5-turbo";
      case "anthropic":
        return "e.g., claude-3-opus-20240229, claude-3-sonnet-20240229";
      case "grok":
        return "e.g., grok-beta, grok-vision-beta";
      case "deepseek":
        return "e.g., deepseek-chat, deepseek-coder";
      default:
        return "Model identifier as used in API";
    }
  };

  const addNewModel = async (providerKey: string) => {
    const modelForm = newModelForm[providerKey];
    if (!modelForm?.modelId || !modelForm?.displayName) return;

    try {
      const response = await enhancedApiService.request(
        "/models/admin/models",
        {
          method: "POST",
          body: JSON.stringify({
            model_id: modelForm.modelId,
            provider: providerKey,
            display_name: modelForm.displayName,
            description: `${modelForm.displayName} model from ${providerKey}`,
            is_active: true,
            supports_streaming: true,
            supports_function_calling: false,
            supports_vision: false,
            context_window: 128000,
          }),
        }
      );

      if (response) {
        // Refresh models and reset form
        await loadModels();
        setNewModelForm((prev) => ({
          ...prev,
          [providerKey]: {
            modelId: "",
            displayName: "",
            show: false,
          },
        }));
      }
    } catch (error) {
      addError(error, "api", `Failed to add model ${modelForm.displayName}`);
    }
  };

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
      {/* Header */}
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

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setAddingNewProvider(!addingNewProvider)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors text-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add Provider</span>
          </button>
          <button
            onClick={loadModels}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <div className="text-sm text-gray-600 dark:text-gray-400">
        Configure AI providers and manage their available models. Each provider
        can have multiple models that can be enabled or disabled individually.
      </div>

      {/* Add New Provider Form */}
      {addingNewProvider && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Add New Provider
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Provider ID
              </label>
              <input
                type="text"
                value={newProviderForm.provider}
                onChange={(e) =>
                  setNewProviderForm((prev) => ({
                    ...prev,
                    provider: e.target.value,
                  }))
                }
                placeholder="e.g., groq, mistral"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Display Name
              </label>
              <input
                type="text"
                value={newProviderForm.display_name}
                onChange={(e) =>
                  setNewProviderForm((prev) => ({
                    ...prev,
                    display_name: e.target.value,
                  }))
                }
                placeholder="e.g., Groq, Mistral AI"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                API Base URL
              </label>
              <input
                type="url"
                value={newProviderForm.api_base_url}
                onChange={(e) =>
                  setNewProviderForm((prev) => ({
                    ...prev,
                    api_base_url: e.target.value,
                  }))
                }
                placeholder="https://api.example.com/v1"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
          <div className="flex items-center space-x-3 mt-4">
            <button
              onClick={() => {
                // Add the new provider to formData and allProviders
                const newProvider = {
                  ...newProviderForm,
                  is_active: true,
                  max_requests_per_minute: 60,
                  max_tokens_per_request: 64000,
                  has_api_key: false,
                };
                setFormData((prev) => ({
                  ...prev,
                  [newProviderForm.provider]: newProvider,
                }));
                setNewProviderForm({
                  provider: "",
                  display_name: "",
                  api_base_url: "",
                });
                setAddingNewProvider(false);
              }}
              disabled={
                !newProviderForm.provider ||
                !newProviderForm.display_name ||
                !newProviderForm.api_base_url
              }
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-md transition-colors"
            >
              Add Provider
            </button>
            <button
              onClick={() => {
                setNewProviderForm({
                  provider: "",
                  display_name: "",
                  api_base_url: "",
                });
                setAddingNewProvider(false);
              }}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Provider Cards with Integrated Models */}
      <div className="space-y-6">
        {allProviders.map((provider) => {
          const isEditing = editingProvider === provider.provider;
          const config = formData[provider.provider] || provider;
          const providerModels = models.filter(
            (model) => model.provider === provider.provider
          );
          const isExpanded = expandedProviders.has(provider.provider);
          const showNewModelForm =
            newModelForm[provider.provider]?.show || false;

          return (
            <div
              key={provider.provider}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              {/* Provider Header */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
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
                        {provider.provider} • {providerModels.length} models
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {provider.has_api_key && (
                      <div className="flex items-center text-green-600 dark:text-green-400">
                        <Key className="w-4 h-4" />
                      </div>
                    )}
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        config.is_active
                          ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                          : "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
                      }`}
                    >
                      {config.is_active ? "Active" : "Inactive"}
                    </span>
                    <button
                      onClick={() => handleEditProvider(provider.provider)}
                      className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Quick Stats */}
                {!isEditing && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">
                        Status:
                      </span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {config.is_active ? "Active" : "Inactive"}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">
                        Models:
                      </span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {
                          providerModels.filter((m) => m.is_active !== false)
                            .length
                        }{" "}
                        / {providerModels.length}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">
                        Rate Limit:
                      </span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {config.max_requests_per_minute}/min
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">
                        Max Tokens:
                      </span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {config.max_tokens_per_request?.toLocaleString()}
                      </span>
                    </div>
                  </div>
                )}
              </div>
              {/* Provider Configuration */}
              {isEditing && (
                <div className="p-6 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
                  <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    Provider Configuration
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* API Key */}
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        API Key
                      </label>
                      <div className="flex rounded-md shadow-sm">
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
                          className="px-3 py-2 border border-l-0 border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-600 text-gray-500 dark:text-gray-400 rounded-r-md hover:bg-gray-100 dark:hover:bg-gray-500 transition-colors"
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
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        API Base URL
                      </label>
                      <div className="flex items-center">
                        <Globe className="w-4 h-4 text-gray-400 mr-2" />
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
                          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      </div>
                    </div>

                    {/* Organization ID (for OpenAI) */}
                    {provider.provider === "openai" && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
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

                    {/* Rate Limits */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
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
                        min="1"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
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
                        min="1"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>

                    {/* Active Checkbox */}
                    <div className="md:col-span-2">
                      <label className="flex items-center space-x-2">
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
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          Provider Active
                        </span>
                      </label>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-end space-x-3 mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
                    <button
                      onClick={() => setEditingProvider(null)}
                      className="px-6 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors focus:ring-2 focus:ring-blue-500"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleSaveProvider(provider.provider)}
                      className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors focus:ring-2 focus:ring-blue-500"
                    >
                      <Save className="w-4 h-4" />
                      <span>Save Configuration</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Models Section */}
              <div className="border-t border-gray-200 dark:border-gray-700">
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
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                      Models ({providerModels.length})
                    </h4>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {
                        providerModels.filter((m) => m.is_active !== false)
                          .length
                      }{" "}
                      active
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setNewModelForm((prev) => ({
                          ...prev,
                          [provider.provider]: {
                            modelId: "",
                            displayName: "",
                            show: !showNewModelForm,
                          },
                        }));
                      }}
                      className="flex items-center space-x-1 px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors text-sm"
                    >
                      <Plus className="w-3 h-3" />
                      <span>Add Model</span>
                    </button>
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                </button>

                {/* Models List */}
                {isExpanded && (
                  <div className="border-t border-gray-200 dark:border-gray-700">
                    {/* Add New Model Form */}
                    {showNewModelForm && (
                      <div className="p-4 bg-green-50 dark:bg-green-900/20 border-b border-gray-200 dark:border-gray-700">
                        <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                          Add New Model to {config.display_name}
                        </h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                              Model ID (API Format)
                            </label>
                            <input
                              type="text"
                              value={
                                newModelForm[provider.provider]?.modelId || ""
                              }
                              onChange={(e) =>
                                setNewModelForm((prev) => ({
                                  ...prev,
                                  [provider.provider]: {
                                    ...prev[provider.provider],
                                    modelId: e.target.value,
                                  },
                                }))
                              }
                              placeholder={getModelIdPlaceholder(
                                provider.provider
                              )}
                              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:text-white text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                              Display Name
                            </label>
                            <input
                              type="text"
                              value={
                                newModelForm[provider.provider]?.displayName ||
                                ""
                              }
                              onChange={(e) =>
                                setNewModelForm((prev) => ({
                                  ...prev,
                                  [provider.provider]: {
                                    ...prev[provider.provider],
                                    displayName: e.target.value,
                                  },
                                }))
                              }
                              placeholder="e.g., GPT-4 Turbo"
                              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500 dark:bg-gray-700 dark:text-white text-sm"
                            />
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 mt-3">
                          <button
                            onClick={() => addNewModel(provider.provider)}
                            disabled={
                              !newModelForm[provider.provider]?.modelId ||
                              !newModelForm[provider.provider]?.displayName
                            }
                            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-md transition-colors text-sm"
                          >
                            Add Model
                          </button>
                          <button
                            onClick={() =>
                              setNewModelForm((prev) => ({
                                ...prev,
                                [provider.provider]: {
                                  modelId: "",
                                  displayName: "",
                                  show: false,
                                },
                              }))
                            }
                            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                        <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                          Enter the exact model ID as used by{" "}
                          {config.display_name}'s API
                        </div>
                      </div>
                    )}

                    {/* Existing Models */}
                    {providerModels.map((model) => (
                      <div
                        key={model.id}
                        className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-3">
                            <h5 className="font-medium text-gray-900 dark:text-white truncate">
                              {model.display_name}
                            </h5>
                            <span
                              className={`px-2 py-1 text-xs rounded-full ${
                                model.is_active !== false
                                  ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                                  : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                              }`}
                            >
                              {model.is_active !== false
                                ? "Active"
                                : "Inactive"}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {model.id}
                          </p>
                          {model.description && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              {model.description}
                            </p>
                          )}
                          <div className="flex items-center space-x-4 mt-2">
                            {model.supports_streaming && (
                              <span className="flex items-center space-x-1 text-xs text-blue-600 dark:text-blue-400">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span>Streaming</span>
                              </span>
                            )}
                            {model.supports_function_calling && (
                              <span className="flex items-center space-x-1 text-xs text-purple-600 dark:text-purple-400">
                                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                                <span>Functions</span>
                              </span>
                            )}
                            {model.supports_vision && (
                              <span className="flex items-center space-x-1 text-xs text-green-600 dark:text-green-400">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span>Vision</span>
                              </span>
                            )}
                            {model.context_window && (
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {model.context_window.toLocaleString()} tokens
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
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

                    {providerModels.length === 0 && (
                      <div className="p-8 text-center">
                        <Database className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                        <p className="text-gray-500 dark:text-gray-400 text-sm">
                          No models configured for this provider
                        </p>
                        <button
                          onClick={() =>
                            setNewModelForm((prev) => ({
                              ...prev,
                              [provider.provider]: {
                                modelId: "",
                                displayName: "",
                                show: true,
                              },
                            }))
                          }
                          className="mt-2 text-blue-600 hover:text-blue-700 dark:text-blue-400 text-sm"
                        >
                          Add your first model
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {allProviders.length === 0 && (
        <div className="text-center py-12">
          <Database className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No providers configured
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Add your first AI provider to get started
          </p>
          <button
            onClick={() => setAddingNewProvider(true)}
            className="flex items-center space-x-2 mx-auto px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Provider</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default UnifiedProviderModelManagement;
