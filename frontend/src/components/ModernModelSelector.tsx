import React, { useState } from "react";
import {
  ChevronDown,
  Zap,
  Brain,
  Shuffle,
  CheckCircle,
  Settings,
} from "lucide-react";
import { ModelSelectionState } from "../types";

interface ModernModelSelectorProps {
  modelSelection: ModelSelectionState;
  onModelSelectionChange: (selection: ModelSelectionState) => void;
  className?: string;
}

// Predefined mode configurations
const MODE_CONFIGS = [
  {
    id: "fastest",
    name: "⚡ Fastest",
    description: "Single best model for speed",
    icon: <Zap className="w-4 h-4" />,
    models: ["gpt-3.5-turbo"],
    debateMode: "single" as const,
    color: "text-yellow-400",
  },
  {
    id: "smartest",
    name: "🧠 Smartest",
    description: "Single best model for accuracy",
    icon: <Brain className="w-4 h-4" />,
    models: ["gpt-4"],
    debateMode: "single" as const,
    color: "text-blue-400",
  },
  {
    id: "consensus",
    name: "🔄 Consensus",
    description: "Multiple models for reliability",
    icon: <Shuffle className="w-4 h-4" />,
    models: ["gpt-4", "claude-3-sonnet"],
    debateMode: "consensus" as const,
    color: "text-primary-teal",
  },
  {
    id: "custom",
    name: "⚙️ Custom",
    description: "Choose your own models",
    icon: <Settings className="w-4 h-4" />,
    models: [],
    debateMode: "custom" as const,
    color: "text-gray-400",
  },
];

const ModernModelSelector: React.FC<ModernModelSelectorProps> = ({
  modelSelection,
  onModelSelectionChange,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Determine current mode based on selection
  const getCurrentMode = () => {
    const { selectedModels, debateMode } = modelSelection;

    if (selectedModels.length === 0) {
      return MODE_CONFIGS.find((m) => m.id === "fastest") || MODE_CONFIGS[0];
    }

    if (selectedModels.length === 1) {
      if (selectedModels[0] === "gpt-3.5-turbo") {
        return MODE_CONFIGS.find((m) => m.id === "fastest") || MODE_CONFIGS[0];
      }
      if (selectedModels[0] === "gpt-4") {
        return MODE_CONFIGS.find((m) => m.id === "smartest") || MODE_CONFIGS[1];
      }
    }

    if (selectedModels.length > 1 && debateMode === "consensus") {
      return MODE_CONFIGS.find((m) => m.id === "consensus") || MODE_CONFIGS[2];
    }

    return MODE_CONFIGS.find((m) => m.id === "custom") || MODE_CONFIGS[3];
  };

  const currentMode = getCurrentMode();

  const handleModeSelect = (mode: (typeof MODE_CONFIGS)[0]) => {
    onModelSelectionChange({
      selectedModels: mode.models,
      debateMode: mode.debateMode as any,
      showDebateProcess: mode.debateMode === "consensus",
    });
    setIsOpen(false);
  };

  const getDisplayName = () => {
    const { selectedModels, debateMode } = modelSelection;

    if (selectedModels.length === 0) {
      return "Select Model";
    }

    if (selectedModels.length === 1) {
      return selectedModels[0]
        .replace(/-/g, " ")
        .replace(/\b\w/g, (l) => l.toUpperCase());
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
          <span className={`model-icon ${currentMode.color}`}>
            {currentMode.icon}
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
            {MODE_CONFIGS.map((mode) => {
              const isSelected = currentMode.id === mode.id;

              return (
                <button
                  key={mode.id}
                  onClick={() => handleModeSelect(mode)}
                  className={`mode-option ${isSelected ? "selected" : ""}`}
                  role="option"
                  aria-selected={isSelected}
                >
                  <div className="mode-option-content">
                    <div className="mode-header">
                      <span className={`mode-icon ${mode.color}`}>
                        {mode.icon}
                      </span>
                      <span className="mode-name">{mode.name}</span>
                      {isSelected && (
                        <CheckCircle className="w-4 h-4 text-primary-teal ml-auto" />
                      )}
                    </div>
                    <p className="mode-description">{mode.description}</p>
                    {mode.models.length > 0 && (
                      <div className="mode-models">
                        {mode.models.slice(0, 2).map((model, index) => (
                          <span key={model} className="model-tag">
                            {model.replace(/-/g, " ")}
                            {index === 0 && mode.models.length > 2 && "..."}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default ModernModelSelector;
