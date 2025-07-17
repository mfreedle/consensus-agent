import React, { useState, useEffect, useCallback } from "react";
import {
  ChevronDown,
  ChevronRight,
  CheckCircle,
  Settings,
  Loader2,
  AlertCircle,
  Eye,
  Code,
  Cpu,
} from "lucide-react";
import { ModelSelectionState, LLMModel } from "../types";
import { enhancedApiService } from "../services/enhancedApi";

interface ModernModelSelectorProps {
  modelSelection: ModelSelectionState;
  onModelSelectionChange: (selection: ModelSelectionState) => void;
  className?: string;
}

// Provider configuration for UI
const PROVIDER_CONFIGS = {
  openai: {
    name: "OpenAI",
    color: "text-green-400",
    bgColor: "bg-green-400/10",
    borderColor: "border-green-400/20",
  },
  grok: {
    name: "Grok (xAI)",
    color: "text-blue-400",
    bgColor: "bg-blue-400/10",
    borderColor: "border-blue-400/20",
  },
  deepseek: {
    name: "DeepSeek",
    color: "text-purple-400",
    bgColor: "bg-purple-400/10",
    borderColor: "border-purple-400/20",
  },
  claude: {
    name: "Anthropic Claude",
    color: "text-orange-400",
    bgColor: "bg-orange-400/10",
    borderColor: "border-orange-400/20",
  },
  anthropic: {
    name: "Anthropic",
    color: "text-orange-400",
    bgColor: "bg-orange-400/10",
    borderColor: "border-orange-400/20",
  },
};

const ModernModelSelector: React.FC<ModernModelSelectorProps> = ({
  modelSelection,
  onModelSelectionChange,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [availableModels, setAvailableModels] = useState<LLMModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedProviders, setExpandedProviders] = useState<Set<string>>(
    new Set()
  );

  // Load available models from backend
  const loadModels = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const modelsResponse = await enhancedApiService.getAvailableModels();

      // Enhanced debug logging
      console.log("🔍 ModernModelSelector: Raw API response", {
        type: typeof modelsResponse,
        isArray: Array.isArray(modelsResponse),
        keys:
          modelsResponse && typeof modelsResponse === "object"
            ? Object.keys(modelsResponse)
            : "N/A",
        response: modelsResponse,
      });

      // Ensure we always have an array - handle various response formats
      let models: LLMModel[] = [];
      if (Array.isArray(modelsResponse)) {
        models = modelsResponse;
        console.log("✅ ModernModelSelector: Using direct array response");
      } else if (modelsResponse && typeof modelsResponse === "object") {
        const responseObj = modelsResponse as any;
        if (Array.isArray(responseObj.data)) {
          models = responseObj.data;
          console.log("✅ ModernModelSelector: Using response.data");
        } else if (Array.isArray(responseObj.models)) {
          models = responseObj.models;
          console.log("✅ ModernModelSelector: Using response.models");
        } else {
          console.warn(
            "❌ ModernModelSelector: Unexpected API response format:",
            modelsResponse
          );
          models = [];
        }
      } else {
        console.warn(
          "❌ ModernModelSelector: Unexpected API response format:",
          modelsResponse
        );
        models = [];
      }

      setAvailableModels(models);

      // Debug logging
      console.log("🔍 ModernModelSelector: Loaded models", {
        count: models.length,
        firstFew: models.slice(0, 3).map((m) => ({
          id: m.id,
          display_name: m.display_name,
          is_active: m.is_active,
        })),
      });

      // Auto-expand all providers to show models by default
      const providers = Array.from(new Set(models.map((m) => m.provider)));
      setExpandedProviders(new Set(providers));
      console.log("🔍 ModernModelSelector: Expanded providers", providers);

      // Auto-select first available models if none selected
      if (modelSelection.selectedModels.length === 0 && models.length > 0) {
        const defaultModels = models.slice(0, 2).map((m) => m.id);

        console.log(
          "🔍 ModernModelSelector: Auto-selecting models",
          defaultModels
        );

        if (defaultModels.length > 0) {
          onModelSelectionChange({
            selectedModels: defaultModels,
            debateMode: defaultModels.length > 1 ? "consensus" : "single",
            showDebateProcess: defaultModels.length > 1,
          });
        }
      }
    } catch (err) {
      console.error("Failed to load models:", err);
      setError("Failed to load models");
      // Set fallback models
      setAvailableModels([
        {
          id: "grok-3-latest",
          provider: "grok",
          display_name: "Grok 3 Latest",
          description: "Latest Grok 3 model with enhanced reasoning",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: false,
          supports_vision: false,
          context_window: 128000,
        },
        {
          id: "grok-3-fast-latest",
          provider: "grok",
          display_name: "Grok 3 Fast Latest",
          description: "Faster version of Grok 3 with optimized performance",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: false,
          supports_vision: false,
          context_window: 128000,
        },
        {
          id: "grok-3-mini-latest",
          provider: "grok",
          display_name: "Grok 3 Mini Latest",
          description: "Compact version of Grok 3 for efficient tasks",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: false,
          supports_vision: false,
          context_window: 64000,
        },
        {
          id: "grok-3-mini-fast-latest",
          provider: "grok",
          display_name: "Grok 3 Mini Fast Latest",
          description: "Fastest and most efficient Grok 3 variant",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: false,
          supports_vision: false,
          context_window: 64000,
        },
        {
          id: "gpt-4.1",
          provider: "openai",
          display_name: "GPT-4.1",
          description: "Enhanced GPT-4 with improved reasoning capabilities",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: true,
          supports_vision: true,
          context_window: 128000,
        },
        {
          id: "gpt-4.1-mini",
          provider: "openai",
          display_name: "GPT-4.1 Mini",
          description: "Efficient version of GPT-4.1 for faster responses",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: true,
          supports_vision: true,
          context_window: 128000,
        },
        {
          id: "o3",
          provider: "openai",
          display_name: "O3",
          description:
            "OpenAI's latest reasoning model with advanced problem-solving",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: true,
          supports_vision: false,
          context_window: 200000,
        },
        {
          id: "o3-mini",
          provider: "openai",
          display_name: "O3 Mini",
          description: "Compact version of O3 for efficient reasoning tasks",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: true,
          supports_vision: false,
          context_window: 128000,
        },
        {
          id: "deepseek-chat",
          provider: "deepseek",
          display_name: "DeepSeek Chat",
          description: "DeepSeek's conversational AI model",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: true,
          supports_vision: false,
          context_window: 64000,
        },
        {
          id: "deepseek-reasoner",
          provider: "deepseek",
          display_name: "DeepSeek Reasoner",
          description: "DeepSeek's advanced reasoning model",
          is_active: true,
          supports_streaming: true,
          supports_function_calling: true,
          supports_vision: false,
          context_window: 64000,
        },
      ] as LLMModel[]);

      // Auto-expand providers for fallback models too
      setExpandedProviders(new Set(["grok", "openai", "deepseek", "claude"]));
    } finally {
      setIsLoading(false);
    }
  }, [modelSelection.selectedModels.length, onModelSelectionChange]);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  // Helper function to get model display name
  const getModelDisplayName = useCallback(
    (modelId: string) => {
      const modelsArray = Array.isArray(availableModels) ? availableModels : [];
      const model = modelsArray.find((m) => m.id === modelId);
      return (
        model?.display_name ||
        modelId.replace(/-/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())
      );
    },
    [availableModels]
  );

  // Group models by provider
  const groupedModels = React.useMemo(() => {
    const groups: Record<string, LLMModel[]> = {};

    // Ensure availableModels is always an array
    const modelsArray = Array.isArray(availableModels) ? availableModels : [];

    modelsArray.forEach((model) => {
      if (!groups[model.provider]) {
        groups[model.provider] = [];
      }
      groups[model.provider].push(model);
    });

    // Sort models within each provider by display_name
    Object.keys(groups).forEach((provider) => {
      groups[provider].sort((a, b) =>
        a.display_name.localeCompare(b.display_name)
      );
    });

    return groups;
  }, [availableModels]);

  const handleModelToggle = (modelId: string) => {
    const isSelected = modelSelection.selectedModels.includes(modelId);
    let newSelectedModels: string[];

    if (isSelected) {
      newSelectedModels = modelSelection.selectedModels.filter(
        (id) => id !== modelId
      );
    } else {
      newSelectedModels = [...modelSelection.selectedModels, modelId];
    }

    // Ensure at least one model is selected
    if (newSelectedModels.length === 0) {
      return;
    }

    const newDebateMode = newSelectedModels.length > 1 ? "consensus" : "single";

    onModelSelectionChange({
      selectedModels: newSelectedModels,
      debateMode: newDebateMode,
      showDebateProcess: newSelectedModels.length > 1,
    });
  };

  const toggleProvider = (provider: string) => {
    const newExpanded = new Set(expandedProviders);
    if (newExpanded.has(provider)) {
      newExpanded.delete(provider);
    } else {
      newExpanded.add(provider);
    }
    setExpandedProviders(newExpanded);
  };

  const getDisplayName = () => {
    const { selectedModels, debateMode } = modelSelection;

    if (selectedModels.length === 0) {
      return "Select Model";
    }

    if (selectedModels.length === 1) {
      return getModelDisplayName(selectedModels[0]);
    }

    if (debateMode === "consensus") {
      return `Consensus (${selectedModels.length} models)`;
    }

    return `Custom (${selectedModels.length} models)`;
  };

  return (
    <div className={`model-selector-container ${className}`}>
      {/* Current Selection Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="model-selector-button"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-label={`Current model: ${getDisplayName()}`}
      >
        <div className="model-selector-content">
          <span className="model-icon text-primary-teal">
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Settings className="w-4 h-4" />
            )}
          </span>
          <span className="model-name">{getDisplayName()}</span>
        </div>
        <ChevronDown className={`chevron ${isOpen ? "rotated" : ""}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          <div
            className="model-selector-overlay"
            onClick={() => setIsOpen(false)}
          />
          <div className="model-selector-dropdown" role="listbox">
            {/* Error State */}
            {error && (
              <div className="error-message">
                <AlertCircle className="w-4 h-4 text-red-400" />
                <span className="text-red-400 text-sm">{error}</span>
                <button
                  onClick={loadModels}
                  className="text-primary-teal text-sm hover:underline ml-2"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="loading-state">
                <Loader2 className="w-4 h-4 animate-spin text-primary-teal" />
                <span className="text-sm text-text-muted">
                  Loading models...
                </span>
              </div>
            )}

            {/* Provider Groups */}
            {!isLoading && Object.keys(groupedModels).length > 0 && (
              <div className="providers-section">
                <div className="section-header">
                  <span className="section-title">Choose Models</span>
                  <span className="selected-count">
                    {modelSelection.selectedModels.length} selected
                  </span>
                </div>

                {Object.entries(groupedModels).map(([provider, models]) => {
                  const isExpanded = expandedProviders.has(provider);
                  const providerConfig =
                    PROVIDER_CONFIGS[provider as keyof typeof PROVIDER_CONFIGS];
                  const selectedModelsInProvider = models.filter((m) =>
                    modelSelection.selectedModels.includes(m.id)
                  ).length;

                  return (
                    <div key={provider} className="provider-group">
                      <button
                        onClick={() => toggleProvider(provider)}
                        className="provider-header"
                      >
                        <div className="provider-info">
                          <ChevronRight
                            className={`provider-chevron ${
                              isExpanded ? "expanded" : ""
                            }`}
                          />
                          <span
                            className={`provider-name ${
                              providerConfig?.color || "text-text-primary"
                            }`}
                          >
                            {providerConfig?.name || provider}
                          </span>
                          <span className="model-count">({models.length})</span>
                        </div>
                        {selectedModelsInProvider > 0 && (
                          <span className="selected-badge">
                            {selectedModelsInProvider} selected
                          </span>
                        )}
                      </button>

                      {isExpanded && (
                        <div className="provider-models">
                          {models.map((model) => {
                            const isSelected =
                              modelSelection.selectedModels.includes(model.id);
                            const isActive = model.is_active !== false;

                            return (
                              <button
                                key={model.id}
                                onClick={() => handleModelToggle(model.id)}
                                disabled={!isActive}
                                className={`model-item ${
                                  isSelected ? "selected" : ""
                                } ${!isActive ? "disabled" : ""}`}
                              >
                                <div className="model-item-content">
                                  <div className="model-info">
                                    <span className="model-display-name">
                                      {model.display_name}
                                    </span>
                                    {model.context_window && (
                                      <span className="model-context">
                                        {(model.context_window / 1000).toFixed(
                                          0
                                        )}
                                        k ctx
                                      </span>
                                    )}
                                  </div>

                                  <div className="model-capabilities">
                                    {model.supports_vision && (
                                      <div title="Vision support">
                                        <Eye className="w-3 h-3 text-blue-400" />
                                      </div>
                                    )}
                                    {model.supports_function_calling && (
                                      <div title="Function calling">
                                        <Code className="w-3 h-3 text-green-400" />
                                      </div>
                                    )}
                                    {model.supports_streaming && (
                                      <div title="Streaming support">
                                        <Cpu className="w-3 h-3 text-orange-400" />
                                      </div>
                                    )}
                                  </div>

                                  {isSelected && (
                                    <CheckCircle className="w-4 h-4 text-primary-teal" />
                                  )}

                                  {!isActive && (
                                    <span className="inactive-badge">
                                      Inactive
                                    </span>
                                  )}
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Current Selection Summary */}
            {!isLoading && modelSelection.selectedModels.length > 0 && (
              <div className="selection-summary">
                <div className="summary-header">Current Selection</div>
                <div className="summary-content">
                  <div className="selected-models">
                    {modelSelection.selectedModels.map((modelId) => (
                      <span key={modelId} className="selected-model-tag">
                        {getModelDisplayName(modelId)}
                      </span>
                    ))}
                  </div>
                  <div className="summary-stats">
                    <span>{modelSelection.selectedModels.length} models</span>
                    <span>•</span>
                    <span>{modelSelection.debateMode} mode</span>
                    {modelSelection.showDebateProcess && (
                      <>
                        <span>•</span>
                        <span>Process visible</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ModernModelSelector;
