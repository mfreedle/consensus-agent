import React from "react";
import { Bot, Zap } from "lucide-react";

interface ConsensusProcessingIndicatorProps {
  message?: string;
  phase?: "analyzing" | "processing" | "consensus" | "finalizing";
  progress?: number; // 0-100 for determinate progress, undefined for indeterminate
}

const ConsensusProcessingIndicator: React.FC<
  ConsensusProcessingIndicatorProps
> = ({
  message = "Processing AI consensus...",
  phase = "processing",
  progress,
}) => {
  const getPhaseInfo = () => {
    switch (phase) {
      case "analyzing":
        return {
          icon: <Bot className="w-4 h-4" />,
          text: "Analyzing your request",
        };
      case "processing":
        return {
          icon: <Zap className="w-4 h-4" />,
          text: "Consulting AI models",
        };
      case "consensus":
        return {
          icon: <Bot className="w-4 h-4" />,
          text: "Building consensus",
        };
      case "finalizing":
        return {
          icon: <Zap className="w-4 h-4" />,
          text: "Finalizing response",
        };
      default:
        return { icon: <Bot className="w-4 h-4" />, text: message };
    }
  };

  const phaseInfo = getPhaseInfo();

  return (
    <div
      className="consensus-processing fade-in"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-2">
        {phaseInfo.icon}
        <span className="text-sm text-primary-cyan font-medium">
          {phaseInfo.text}
        </span>
        <div className="consensus-dots" aria-hidden="true">
          <div className="consensus-dot" />
          <div className="consensus-dot" />
          <div className="consensus-dot" />
        </div>
      </div>

      {/* Progress bar */}
      <div className="progress-bar mt-2">
        {progress !== undefined ? (
          <div
            className="progress-fill"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        ) : (
          <div className="progress-fill progress-indeterminate w-1/3" />
        )}
      </div>

      {/* Screen reader text */}
      <span className="sr-only">
        AI consensus in progress. {phaseInfo.text}.
        {progress !== undefined && ` ${progress}% complete.`}
      </span>
    </div>
  );
};

export default ConsensusProcessingIndicator;
