import React, { useState, useEffect } from "react";
import { Check, Settings, Bot, Zap, Brain, Sparkles } from "lucide-react";
import { LLMModel, ModelSelectionState } from "../types";
import { apiService } from "../services/api";

interface ModelSelectionProps {
  selectedModels: string[];
  debateMode: "consensus" | "detailed" | "quick";
  showDebateProcess: boolean;
  onModelSelectionChange: (selection: ModelSelectionState) => void;
  className?: string;
}

const ModelSelection: React.FC<ModelSelectionProps> = ({
  selectedModels,
  debateMode,
  showDebateProcess,
  onModelSelectionChange,
  className = "",
}) => {
  const [availableModels, setAvailableModels] = useState<LLMModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    const loadAvailableModels = async () => {
      setIsLoading(true);
      try {
        const result = await apiService.getAvailableModels();
        if (result.data) {
          setAvailableModels(result.data);

          // Auto-select active models if none selected
          if (selectedModels.length === 0) {
            const activeModels = result.data
              .filter((model) => model.is_active !== false)
              .slice(0, 2) // Select first 2 active models by default
              .map((model) => model.id);

            onModelSelectionChange({
              selectedModels: activeModels,
              debateMode,
              showDebateProcess,
            });
          }
        }
      } catch (error) {
        console.error("Failed to load models:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadAvailableModels();
  }, [
    selectedModels.length,
    debateMode,
    showDebateProcess,
    onModelSelectionChange,
  ]);

  const handleModelToggle = (modelId: string) => {
    let newSelection = [...selectedModels];

    if (newSelection.includes(modelId)) {
      newSelection = newSelection.filter((id) => id !== modelId);
    } else {
      newSelection.push(modelId);
    }

    // Ensure at least one model is selected
    if (newSelection.length === 0) {
      return;
    }

    onModelSelectionChange({
      selectedModels: newSelection,
      debateMode,
      showDebateProcess,
    });
  };

  const handleDebateModeChange = (mode: "consensus" | "detailed" | "quick") => {
    onModelSelectionChange({
      selectedModels,
      debateMode: mode,
      showDebateProcess,
    });
  };

  const handleShowDebateToggle = () => {
    onModelSelectionChange({
      selectedModels,
      debateMode,
      showDebateProcess: !showDebateProcess,
    });
  };

  const getModelIcon = (provider: string) => {
    switch (provider) {
      case "openai":
        return <Brain className="w-4 h-4" />;
      case "grok":
        return <Zap className="w-4 h-4" />;
      case "claude":
        return <Sparkles className="w-4 h-4" />;
      default:
        return <Bot className="w-4 h-4" />;
    }
  };

  const getProviderColor = (provider: string) => {
    switch (provider) {
      case "openai":
        return "text-primary-cyan border-primary-cyan/30 bg-primary-cyan/10";
      case "grok":
        return "text-primary-blue border-primary-blue/30 bg-primary-blue/10";
      case "claude":
        return "text-primary-purple border-primary-purple/30 bg-primary-purple/10";
      default:
        return "text-gray-400 border-gray-600 bg-gray-800/50";
    }
  };

  if (isLoading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-4 space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-primary-cyan">
          Model Selection
        </h3>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="p-1 rounded-lg hover:bg-primary-teal/10 transition-colors"
        >
          <Settings className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {/* Model Selection */}
      <div className="space-y-2">
        <div className="text-xs text-gray-400 mb-2">
          Select models for consensus ({selectedModels.length} selected)
        </div>
        {availableModels.map((model) => {
          const isSelected = selectedModels.includes(model.id);
          const isActive = model.is_active !== false;

          return (
            <div
              key={model.id}
              className={`
                relative p-3 rounded-lg border transition-all cursor-pointer
                ${
                  isSelected
                    ? `${getProviderColor(
                        model.provider
                      )} ring-1 ring-primary-cyan/50`
                    : "border-gray-600 bg-gray-800/50 hover:border-gray-500"
                }
                ${!isActive ? "opacity-50" : ""}
              `}
              onClick={() => isActive && handleModelToggle(model.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div
                    className={`p-1.5 rounded ${getProviderColor(
                      model.provider
                    )}`}
                  >
                    {getModelIcon(model.provider)}
                  </div>
                  <div>
                    <h4 className="font-medium text-white text-sm">
                      {model.display_name}
                    </h4>
                    {model.description && (
                      <p className="text-xs text-gray-400">
                        {model.description}
                      </p>
                    )}
                  </div>
                </div>

                {isActive && (
                  <div
                    className={`
                    w-5 h-5 rounded border-2 flex items-center justify-center
                    ${
                      isSelected
                        ? "bg-primary-cyan border-primary-cyan"
                        : "border-gray-500"
                    }
                  `}
                  >
                    {isSelected && <Check className="w-3 h-3 text-black" />}
                  </div>
                )}

                {!isActive && (
                  <div className="text-xs text-gray-500">Inactive</div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="space-y-4 pt-4 border-t border-gray-600">
          {/* Debate Mode */}
          <div>
            <div className="text-xs text-gray-400 mb-2">Consensus Mode</div>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: "quick", label: "Quick", desc: "Fast consensus" },
                {
                  id: "consensus",
                  label: "Standard",
                  desc: "Balanced approach",
                },
                { id: "detailed", label: "Detailed", desc: "Deep analysis" },
              ].map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => handleDebateModeChange(mode.id as any)}
                  className={`
                    p-2 rounded-lg text-xs font-medium transition-all
                    ${
                      debateMode === mode.id
                        ? "bg-primary-cyan text-black"
                        : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                    }
                  `}
                >
                  <div>{mode.label}</div>
                  <div className="text-xs opacity-75">{mode.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Show Debate Process Toggle */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-medium text-white">
                Show Debate Process
              </div>
              <div className="text-xs text-gray-400">
                View model discussions in real-time
              </div>
            </div>
            <button
              onClick={handleShowDebateToggle}
              className={`
                relative inline-flex h-5 w-9 items-center rounded-full transition-colors
                ${showDebateProcess ? "bg-primary-cyan" : "bg-gray-600"}
              `}
            >
              <span
                className={`
                  inline-block h-3 w-3 transform rounded-full bg-white transition-transform
                  ${showDebateProcess ? "translate-x-5" : "translate-x-1"}
                `}
              />
            </button>
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="text-xs text-gray-400 bg-gray-800/50 p-3 rounded-lg">
        <div className="font-medium text-gray-300 mb-1">Current Setup:</div>
        <div>• {selectedModels.length} models selected</div>
        <div>• {debateMode} consensus mode</div>
        <div>• Debate process {showDebateProcess ? "visible" : "hidden"}</div>
      </div>
    </div>
  );
};

export default ModelSelection;
