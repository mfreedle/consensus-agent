import React, { useState, useEffect } from "react";
import {
  Bot,
  Brain,
  Zap,
  Sparkles,
  MessageCircle,
  TrendingUp,
  Clock,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { DebateStep, ConsensusData } from "../types";

interface ConsensusDebateVisualizerProps {
  consensusData?: ConsensusData;
  isDebating?: boolean;
  debateSteps?: DebateStep[];
  className?: string;
}

const ConsensusDebateVisualizer: React.FC<ConsensusDebateVisualizerProps> = ({
  consensusData,
  isDebating = false,
  debateSteps = [],
  className = "",
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [visibleSteps, setVisibleSteps] = useState(0);

  useEffect(() => {
    if (isDebating && debateSteps.length > 0) {
      // Animate steps appearing one by one
      const timer = setTimeout(() => {
        setVisibleSteps((prev) => Math.min(prev + 1, debateSteps.length));
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [isDebating, debateSteps.length, visibleSteps]);

  const getModelIcon = (modelName: string) => {
    const lowerName = modelName.toLowerCase();
    if (lowerName.includes("gpt") || lowerName.includes("openai")) {
      return <Brain className="w-4 h-4" />;
    } else if (lowerName.includes("grok")) {
      return <Zap className="w-4 h-4" />;
    } else if (lowerName.includes("claude")) {
      return <Sparkles className="w-4 h-4" />;
    }
    return <Bot className="w-4 h-4" />;
  };

  const getModelColor = (modelName: string) => {
    const lowerName = modelName.toLowerCase();
    if (lowerName.includes("gpt") || lowerName.includes("openai")) {
      return {
        bg: "bg-primary-cyan/10",
        border: "border-primary-cyan/30",
        text: "text-primary-cyan",
        accent: "bg-primary-cyan",
      };
    } else if (lowerName.includes("grok")) {
      return {
        bg: "bg-primary-blue/10",
        border: "border-primary-blue/30",
        text: "text-primary-blue",
        accent: "bg-primary-blue",
      };
    } else if (lowerName.includes("claude")) {
      return {
        bg: "bg-primary-purple/10",
        border: "border-primary-purple/30",
        text: "text-primary-purple",
        accent: "bg-primary-purple",
      };
    }
    return {
      bg: "bg-gray-800/50",
      border: "border-gray-600",
      text: "text-gray-400",
      accent: "bg-gray-600",
    };
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-primary-green";
    if (confidence >= 0.6) return "text-primary-yellow";
    return "text-primary-coral";
  };

  const getConfidenceWidth = (confidence: number) => {
    return `${Math.round(confidence * 100)}%`;
  };

  if (!consensusData && !isDebating && debateSteps.length === 0) {
    return null;
  }

  return (
    <div
      className={`border border-gray-600 rounded-lg bg-gray-800/50 ${className}`}
    >
      {/* Header */}
      <div
        className="p-4 border-b border-gray-600 cursor-pointer flex items-center justify-between"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-teal/10 rounded-lg border border-primary-teal/30">
            <MessageCircle className="w-5 h-5 text-primary-teal" />
          </div>
          <div>
            <h3 className="font-semibold text-white">
              {isDebating ? "Consensus in Progress..." : "Consensus Analysis"}
            </h3>
            <p className="text-sm text-gray-400">
              {isDebating
                ? `Processing through ${debateSteps.length} debate steps...`
                : consensusData
                ? `Confidence: ${Math.round(
                    (consensusData.confidence_score || 0) * 100
                  )}%`
                : "Analysis complete"}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {isDebating && (
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-primary-cyan rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-primary-blue rounded-full animate-pulse delay-100"></div>
              <div className="w-2 h-2 bg-primary-teal rounded-full animate-pulse delay-200"></div>
            </div>
          )}
          {isExpanded ? (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="p-4 space-y-4">
          {/* Debate Steps */}
          {(isDebating || debateSteps.length > 0) && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-gray-400" />
                <h4 className="font-medium text-gray-300">Debate Process</h4>
              </div>

              <div className="space-y-3 max-h-60 overflow-y-auto">
                {debateSteps.slice(0, visibleSteps).map((step, index) => {
                  const colors = getModelColor(step.model_name);

                  return (
                    <div
                      key={step.id}
                      className={`
                        p-3 rounded-lg border transition-all duration-500 transform
                        ${colors.bg} ${colors.border}
                        ${
                          index < visibleSteps
                            ? "opacity-100 translate-y-0"
                            : "opacity-0 translate-y-2"
                        }
                      `}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div
                            className={`p-1.5 rounded ${colors.bg} ${colors.border} border`}
                          >
                            {getModelIcon(step.model_name)}
                          </div>
                          <div>
                            <div
                              className={`font-medium text-sm ${colors.text}`}
                            >
                              {step.model_name}
                            </div>
                            <div className="text-xs text-gray-400">
                              Step {step.step_number}
                            </div>
                          </div>
                        </div>

                        <div className="text-right">
                          <div
                            className={`text-sm font-medium ${getConfidenceColor(
                              step.confidence
                            )}`}
                          >
                            {Math.round(step.confidence * 100)}%
                          </div>
                          <div className="text-xs text-gray-400">
                            confidence
                          </div>
                        </div>
                      </div>

                      <div className="text-sm text-gray-300 mb-2">
                        {step.content}
                      </div>

                      {step.reasoning && (
                        <div className="text-xs text-gray-400 italic">
                          Reasoning: {step.reasoning}
                        </div>
                      )}

                      {/* Confidence Bar */}
                      <div className="mt-2">
                        <div className="w-full bg-gray-700 rounded-full h-1">
                          <div
                            className={`h-1 rounded-full transition-all duration-1000 ${colors.accent}`}
                            style={{
                              width: getConfidenceWidth(step.confidence),
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}

                {isDebating && visibleSteps < debateSteps.length && (
                  <div className="text-center py-2">
                    <div className="animate-spin w-4 h-4 border-2 border-primary-teal border-t-transparent rounded-full mx-auto"></div>
                    <div className="text-xs text-gray-400 mt-1">
                      Processing next step...
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Model Responses */}
          {consensusData && (
            <div className="space-y-4">
              {/* Individual Model Responses */}
              {consensusData.openai_response && (
                <div className="p-3 bg-primary-cyan/10 rounded-lg border border-primary-cyan/30">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Brain className="w-4 h-4 text-primary-cyan" />
                      <span className="font-medium text-primary-cyan">
                        OpenAI Response
                      </span>
                    </div>
                    <div
                      className={`text-sm font-medium ${getConfidenceColor(
                        consensusData.openai_response.confidence
                      )}`}
                    >
                      {Math.round(
                        consensusData.openai_response.confidence * 100
                      )}
                      %
                    </div>
                  </div>
                  <div className="text-sm text-gray-300 mb-2">
                    {consensusData.openai_response.content}
                  </div>
                  <div className="text-xs text-gray-400 italic">
                    {consensusData.openai_response.reasoning}
                  </div>
                </div>
              )}

              {consensusData.grok_response && (
                <div className="p-3 bg-primary-blue/10 rounded-lg border border-primary-blue/30">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Zap className="w-4 h-4 text-primary-blue" />
                      <span className="font-medium text-primary-blue">
                        Grok Response
                      </span>
                    </div>
                    <div
                      className={`text-sm font-medium ${getConfidenceColor(
                        consensusData.grok_response.confidence
                      )}`}
                    >
                      {Math.round(consensusData.grok_response.confidence * 100)}
                      %
                    </div>
                  </div>
                  <div className="text-sm text-gray-300 mb-2">
                    {consensusData.grok_response.content}
                  </div>
                  <div className="text-xs text-gray-400 italic">
                    {consensusData.grok_response.reasoning}
                  </div>
                </div>
              )}

              {/* Consensus Summary */}
              <div className="p-4 bg-primary-teal/10 rounded-lg border border-primary-teal/30">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5 text-primary-teal" />
                    <span className="font-semibold text-primary-teal">
                      Final Consensus
                    </span>
                  </div>
                  <div
                    className={`text-lg font-bold ${getConfidenceColor(
                      consensusData.confidence_score
                    )}`}
                  >
                    {Math.round(consensusData.confidence_score * 100)}%
                  </div>
                </div>

                <div className="text-gray-300 mb-3">
                  {consensusData.final_consensus}
                </div>

                <div className="text-sm text-gray-400 mb-3">
                  <strong>Reasoning:</strong> {consensusData.reasoning}
                </div>

                {/* Debate Points */}
                {consensusData.debate_points &&
                  consensusData.debate_points.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-gray-300 mb-2">
                        Key Debate Points:
                      </div>
                      <ul className="space-y-1">
                        {consensusData.debate_points.map((point, index) => (
                          <li
                            key={index}
                            className="text-xs text-gray-400 flex items-start"
                          >
                            <span className="w-1 h-1 bg-primary-teal rounded-full mt-2 mr-2 flex-shrink-0"></span>
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                {/* Overall Confidence Bar */}
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Overall Confidence</span>
                    <span>
                      {Math.round(consensusData.confidence_score * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-primary-cyan to-primary-teal transition-all duration-1000"
                      style={{
                        width: getConfidenceWidth(
                          consensusData.confidence_score
                        ),
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ConsensusDebateVisualizer;
