import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2, Upload, Bot, User } from "lucide-react";
import { useForm } from "react-hook-form";
import { ConsensusResponse, apiService } from "../services/api";
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

  const onSubmit = async (data: MessageForm) => {
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

      // Use real API call to backend
      console.log("Sending message to backend API...");

      const apiRequest = {
        message: data.message,
        session_id: sessionId ? parseInt(sessionId) : undefined,
        use_consensus:
          modelSelection?.selectedModels &&
          modelSelection.selectedModels.length > 1,
        selected_models: modelSelection?.selectedModels || ["gpt-4o"],
      };

      const response = await apiService.sendMessage(apiRequest);

      if (response.error) {
        throw new Error(response.error);
      }

      if (response.data) {
        const backendMessage = response.data.message;
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
        if (response.data.session && !sessionId) {
          onSessionCreated(response.data.session.id.toString());
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // TODO: Show error toast
    } finally {
      setIsLoading(false);
    }
  };
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
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && !sessionId ? (
          // Welcome Screen
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <img
                src="/logo.svg"
                alt="Consensus Agent"
                className="w-24 h-24 mx-auto mb-6 opacity-50"
              />
              <h2 className="text-2xl font-bold text-primary-cyan mb-2">
                Welcome to Consensus Agent
              </h2>
              <p className="text-gray-400 max-w-md">
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
                  className={`flex max-w-4xl ${
                    message.role === "user" ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`flex-shrink-0 ${
                      message.role === "user" ? "ml-3" : "mr-3"
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === "user"
                          ? "bg-primary-teal/20"
                          : "bg-primary-blue/20"
                      }`}
                    >
                      {message.role === "user" ? (
                        <User className="w-4 h-4 text-primary-cyan" />
                      ) : (
                        <Bot className="w-4 h-4 text-primary-azure" />
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
                      className={`px-4 py-3 rounded-2xl ${
                        message.role === "user"
                          ? "bg-primary-teal/20 text-white"
                          : "bg-bg-dark-secondary border border-primary-teal/20 text-white"
                      }`}
                    >
                      <div className="whitespace-pre-wrap">
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
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-primary-blue/20 flex items-center justify-center">
                <Bot className="w-4 h-4 text-primary-azure" />
              </div>
              <div className="bg-bg-dark-secondary border border-primary-teal/20 rounded-2xl px-4 py-3">
                {" "}
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-primary-cyan" />
                  <div className="flex flex-col">
                    <span className="text-sm text-gray-400">
                      {modelSelection?.selectedModels?.length
                        ? `Analyzing with ${modelSelection.selectedModels.length} AI models...`
                        : "Analyzing with multiple AI models..."}
                    </span>
                    {modelSelection?.selectedModels?.length &&
                      modelSelection.selectedModels.length > 0 && (
                        <span className="text-xs text-gray-500">
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
      <div className="border-t border-primary-teal/20 p-6">
        {/* Connection Status */}
        {!isSocketConnected && (
          <div className="mb-3 flex items-center space-x-2 text-sm text-amber-400">
            <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></div>
            <span>Real-time mode unavailable - using HTTP fallback</span>
          </div>
        )}

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="flex items-end space-x-4"
        >
          {/* File Upload Button */}
          <button
            type="button"
            className="flex-shrink-0 p-3 rounded-lg bg-primary-teal/10 hover:bg-primary-teal/20 transition-colors"
          >
            <Upload className="w-5 h-5 text-primary-cyan" />
          </button>

          {/* Message Input */}
          <div className="flex-1">
            <textarea
              {...register("message", { required: "Message is required" })}
              placeholder={
                isSocketConnected
                  ? "Ask anything... Real-time AI consensus analysis enabled."
                  : "Ask anything... Multiple AI models will analyze your question."
              }
              className="w-full px-4 py-3 bg-bg-dark-secondary border border-primary-teal/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-cyan/50 focus:border-primary-cyan text-white placeholder-gray-500 resize-none"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(onSubmit)();
                }
              }}
            />
            {errors.message && (
              <p className="text-red-400 text-sm mt-1">
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
            className="flex-shrink-0 btn-gradient-primary p-3 rounded-lg hover:glow-effect-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5 text-white" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
