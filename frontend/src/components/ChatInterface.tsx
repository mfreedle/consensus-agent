import React, { useState, useRef, useEffect, useCallback } from "react";
import { Send, Loader2, Upload, Bot, User } from "lucide-react";
import { useForm } from "react-hook-form";
import { ConsensusResponse } from "../services/api";
import { enhancedApiService } from "../services/enhancedApi";
import { useErrorHandler } from "../hooks/useErrorHandler";
import { SocketMessage, ModelSelectionState } from "../types";
import ConsensusDebateVisualizer from "./ConsensusDebateVisualizer";

interface ChatInterfaceProps {
  sessionId: string | null;
  onSessionCreated: (sessionId: string) => void;
  socketMessages?: SocketMessage[];
  onSendSocketMessage?: (message: string) => boolean;
  isSocketConnected?: boolean;
  modelSelection?: ModelSelectionState;
}

interface Message {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  session_id: number;
  consensus?: ConsensusResponse;
}

interface MessageForm {
  message: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionId,
  onSessionCreated,
  socketMessages = [],
  onSendSocketMessage,
  isSocketConnected = false,
  modelSelection,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showConsensusDetails, setShowConsensusDetails] = useState<
    number | null
  >(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { addError } = useErrorHandler();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<MessageForm>(); // Mock messages for development
  // Load messages for session - removed mock messages that interfere with real Socket.IO
  useEffect(() => {
    // Clear messages when session changes
    setMessages([]);
  }, [sessionId]); // Add socket messages to the regular messages
  useEffect(() => {
    if (socketMessages.length > 0) {
      const convertedMessages: Message[] = socketMessages.map(
        (socketMsg, index) => ({
          id: Date.now() + index,
          role: socketMsg.role,
          content: socketMsg.content,
          timestamp: socketMsg.timestamp || new Date().toISOString(),
          session_id:
            typeof socketMsg.session_id === "string"
              ? parseInt(socketMsg.session_id)
              : socketMsg.session_id,
          consensus: socketMsg.consensus as ConsensusResponse | undefined,
        })
      );

      setMessages((prev) => {
        // Avoid duplicates by checking if message content already exists
        const existingContents = prev.map((msg) => msg.content);
        const newMessages = convertedMessages.filter(
          (msg) => !existingContents.includes(msg.content)
        );
        return [...prev, ...newMessages];
      });
    }
  }, [socketMessages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const onSubmit = useCallback(
    async (data: MessageForm) => {
      if (!data.message.trim()) return;

      const userMessage: Message = {
        id: Date.now(),
        role: "user",
        content: data.message,
        timestamp: new Date().toISOString(),
        session_id: parseInt(sessionId || "0"),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      reset();

      try {
        // Try to send via Socket.IO first if connected
        if (isSocketConnected && onSendSocketMessage) {
          const socketSent = onSendSocketMessage(data.message);
          if (socketSent) {
            console.log("Message sent via Socket.IO");
            // The response will come through socketMessages
            setIsLoading(false);
            return;
          }
        }

        // Use enhanced API service to backend
        console.log("Sending message to backend API...");

        const apiRequest = {
          message: data.message,
          session_id: sessionId ? parseInt(sessionId) : undefined,
          use_consensus:
            modelSelection?.selectedModels &&
            modelSelection.selectedModels.length > 1,
          selected_models: modelSelection?.selectedModels || ["gpt-4o"],
        };

        const response = await enhancedApiService.sendMessage(apiRequest);

        const backendMessage = response.message;
        const assistantMessage: Message = {
          id: backendMessage.id,
          role: backendMessage.role as "user" | "assistant",
          content: backendMessage.content,
          timestamp: backendMessage.created_at,
          session_id: backendMessage.session_id,
          consensus: backendMessage.consensus_data as
            | ConsensusResponse
            | undefined,
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Update session if created
        if (response.session && !sessionId) {
          onSessionCreated(response.session.id.toString());
        }
      } catch (error) {
        console.error("Error sending message:", error);
        addError(error, "api", "Failed to send message. Please try again.");
      } finally {
        setIsLoading(false);
      }
    },
    [
      sessionId,
      reset,
      isSocketConnected,
      onSendSocketMessage,
      modelSelection,
      onSessionCreated,
      addError,
    ]
  );
  const toggleConsensusDetails = (messageId: number) => {
    setShowConsensusDetails(
      showConsensusDetails === messageId ? null : messageId
    );
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 md:space-y-6">
        {messages.length === 0 && !sessionId ? (
          // Welcome Screen
          <div className="flex items-center justify-center h-full">
            <div className="text-center px-4">
              <img
                src="/logo.svg"
                alt="Consensus Agent"
                className="w-16 h-16 md:w-24 md:h-24 mx-auto mb-4 md:mb-6 opacity-50"
              />
              <h2 className="text-xl md:text-2xl font-bold text-primary-cyan mb-2">
                Welcome to Consensus Agent
              </h2>
              <p className="text-gray-400 max-w-md text-sm md:text-base">
                Experience the power of multi-LLM consensus. Ask any question
                and get insights from multiple AI models working together.
              </p>
            </div>
          </div>
        ) : (
          // Messages
          messages.map((message) => (
            <div key={message.id} className="space-y-4">
              {/* Message */}
              <div
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex max-w-full md:max-w-4xl ${
                    message.role === "user" ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`flex-shrink-0 ${
                      message.role === "user" ? "ml-2 md:ml-3" : "mr-2 md:mr-3"
                    }`}
                  >
                    <div
                      className={`w-6 h-6 md:w-8 md:h-8 rounded-full flex items-center justify-center ${
                        message.role === "user"
                          ? "bg-primary-teal/20"
                          : "bg-primary-blue/20"
                      }`}
                    >
                      {message.role === "user" ? (
                        <User className="w-3 h-3 md:w-4 md:h-4 text-primary-cyan" />
                      ) : (
                        <Bot className="w-3 h-3 md:w-4 md:h-4 text-primary-azure" />
                      )}
                    </div>
                  </div>

                  {/* Message Content */}
                  <div
                    className={`flex flex-col ${
                      message.role === "user" ? "items-end" : "items-start"
                    }`}
                  >
                    <div
                      className={`px-3 py-2 md:px-4 md:py-3 rounded-2xl max-w-[85%] sm:max-w-none ${
                        message.role === "user"
                          ? "bg-primary-teal/20 text-white"
                          : "bg-bg-dark-secondary border border-primary-teal/20 text-white"
                      }`}
                    >
                      <div className="whitespace-pre-wrap text-sm md:text-base">
                        {message.content}
                      </div>
                    </div>{" "}
                    <div className="text-xs text-gray-500 mt-1">
                      {formatTime(message.timestamp)}
                    </div>
                    {/* Consensus Visualization */}
                    {message.consensus && modelSelection?.showDebateProcess && (
                      <div className="mt-3 w-full max-w-2xl">
                        <ConsensusDebateVisualizer
                          consensusData={message.consensus}
                          isDebating={false}
                          className="w-full"
                        />
                      </div>
                    )}
                    {/* Legacy Consensus Details - Show when debate process is hidden */}
                    {message.consensus &&
                      !modelSelection?.showDebateProcess && (
                        <div className="mt-2">
                          <button
                            onClick={() => toggleConsensusDetails(message.id)}
                            className="text-xs text-primary-cyan hover:underline"
                          >
                            {showConsensusDetails === message.id
                              ? "Hide"
                              : "Show"}{" "}
                            Consensus Details
                          </button>

                          {showConsensusDetails === message.id && (
                            <div className="mt-2 p-3 bg-bg-dark rounded-lg border border-primary-teal/20 text-sm space-y-2">
                              <div className="font-medium text-primary-cyan">
                                Consensus Analysis
                              </div>
                              <div className="text-xs text-gray-400">
                                Confidence:{" "}
                                {(
                                  message.consensus.confidence_score * 100
                                ).toFixed(1)}
                                %
                              </div>
                              <div className="text-xs text-gray-300">
                                {message.consensus.reasoning}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2 md:space-x-3">
              <div className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-primary-blue/20 flex items-center justify-center">
                <Bot className="w-3 h-3 md:w-4 md:h-4 text-primary-azure" />
              </div>
              <div className="bg-bg-dark-secondary border border-primary-teal/20 rounded-2xl px-3 py-2 md:px-4 md:py-3">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-3 h-3 md:w-4 md:h-4 animate-spin text-primary-cyan" />
                  <div className="flex flex-col">
                    <span className="text-xs md:text-sm text-gray-400">
                      {modelSelection?.selectedModels?.length
                        ? `Analyzing with ${modelSelection.selectedModels.length} AI models...`
                        : "Analyzing with multiple AI models..."}
                    </span>
                    {modelSelection?.selectedModels?.length &&
                      modelSelection.selectedModels.length > 0 && (
                        <span className="text-xs text-gray-500 hidden sm:inline">
                          Mode: {modelSelection.debateMode}
                        </span>
                      )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>{" "}
      {/* Input Area */}
      <div className="border-t border-primary-teal/20 p-4 md:p-6">
        {/* Connection Status */}
        {!isSocketConnected && (
          <div className="mb-3 flex items-center space-x-2 text-xs md:text-sm text-amber-400">
            <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></div>
            <span className="hidden sm:inline">
              Real-time mode unavailable - using HTTP fallback
            </span>
            <span className="sm:hidden">HTTP mode</span>
          </div>
        )}

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="flex items-end space-x-2 md:space-x-4"
        >
          {/* File Upload Button - Hidden on small screens */}
          <button
            type="button"
            className="hidden sm:flex flex-shrink-0 p-3 rounded-lg bg-primary-teal/10 hover:bg-primary-teal/20 transition-colors"
          >
            <Upload className="w-5 h-5 text-primary-cyan" />
          </button>

          {/* Message Input */}
          <div className="flex-1 relative">
            <textarea
              {...register("message", { required: "Message is required" })}
              placeholder={
                isSocketConnected
                  ? "Ask anything... Real-time AI consensus analysis enabled."
                  : "Ask anything... Multiple AI models will analyze your question."
              }
              className="w-full px-3 md:px-4 py-2 md:py-3 bg-bg-dark-secondary border border-primary-teal/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-cyan/50 focus:border-primary-cyan text-white placeholder-gray-500 resize-none disabled:opacity-50 text-sm md:text-base"
              rows={1}
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(onSubmit)();
                }
              }}
            />
            {isLoading && (
              <div className="absolute right-3 top-2 md:top-3">
                <Loader2 className="w-4 h-4 md:w-5 md:h-5 animate-spin text-primary-cyan" />
              </div>
            )}
            {errors.message && (
              <p className="text-red-400 text-xs md:text-sm mt-1">
                {typeof errors.message === "string"
                  ? errors.message
                  : errors.message.message || "Message is required"}
              </p>
            )}
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="flex-shrink-0 btn-gradient-primary p-2 md:p-3 rounded-lg hover:glow-effect-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 md:w-5 md:h-5 animate-spin text-white" />
            ) : (
              <Send className="w-4 h-4 md:w-5 md:h-5 text-white" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
