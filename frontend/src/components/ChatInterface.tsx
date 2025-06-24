import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2, Upload, Bot, User } from "lucide-react";
import { useForm } from "react-hook-form";
import { ConsensusResponse } from "../services/api";
import { SocketMessage } from "../types";

interface ChatInterfaceProps {
  sessionId: string | null;
  onSessionCreated: (sessionId: string) => void;
  socketMessages?: SocketMessage[];
  onSendSocketMessage?: (message: string) => boolean;
  isSocketConnected?: boolean;
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
  useEffect(() => {
    if (sessionId === "1") {
      setMessages([
        {
          id: 1,
          role: "user",
          content:
            "What are the key ethical considerations when developing AI systems?",
          timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          session_id: 1,
        },
        {
          id: 2,
          role: "assistant",
          content:
            "After analyzing multiple AI perspectives, here are the key ethical considerations for AI development:\n\n1. **Transparency and Explainability**: AI systems should provide clear explanations for their decisions\n2. **Fairness and Bias Mitigation**: Ensuring AI doesn't perpetuate or amplify societal biases\n3. **Privacy Protection**: Safeguarding user data and maintaining confidentiality\n4. **Human Oversight**: Maintaining meaningful human control over AI decisions\n5. **Accountability**: Clear responsibility chains for AI outcomes",
          timestamp: new Date(Date.now() - 3590000).toISOString(),
          session_id: 1,
          consensus: {
            openai_response: {
              content:
                "Focus on transparency, fairness, privacy, and accountability as core pillars.",
              confidence: 0.92,
              reasoning:
                "Based on established AI ethics frameworks and research",
            },
            grok_response: {
              content:
                "Emphasize human oversight and real-world impact assessment.",
              confidence: 0.88,
              reasoning:
                "Real-time analysis of current AI deployment challenges",
            },
            final_consensus:
              "Combined comprehensive approach balancing technical and human factors.",
            confidence_score: 0.9,
            reasoning:
              "High agreement between models on fundamental ethical principles",
            debate_points: [
              "Privacy vs transparency trade-offs",
              "Human oversight vs automation efficiency",
              "Global vs local ethical standards",
            ],
          },
        },
      ]);
    } else {
      setMessages([]);
    }
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
          return;
        }
      }

      // Fallback to HTTP API or simulate for development
      console.log("Using fallback HTTP API or simulation...");
      // TODO: Replace with actual API call to backend
      // Simulate API call with consensus response
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content: `I've analyzed your question "${data.message}" using multiple AI models. Here's the consensus response:\n\nThis is a simulated response that would normally come from the backend after processing through both OpenAI and Grok models, then generating a consensus answer.`,
        timestamp: new Date().toISOString(),
        session_id: parseInt(sessionId || "0"),
        consensus: {
          openai_response: {
            content: "OpenAI perspective on the question",
            confidence: 0.85,
            reasoning: "Based on training data and reasoning",
          },
          grok_response: {
            content: "Grok perspective with real-time insights",
            confidence: 0.82,
            reasoning: "Real-time analysis and current context",
          },
          final_consensus: "Merged insights from both models",
          confidence_score: 0.84,
          reasoning: "Good alignment between model responses",
          debate_points: [
            "Model agreement on core concepts",
            "Slight differences in confidence levels",
            "Real-time vs training data perspectives",
          ],
        },
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Create session if this is the first message
      if (!sessionId) {
        onSessionCreated(Date.now().toString());
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
                    {/* Consensus Details */}
                    {message.consensus && (
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
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-primary-cyan" />
                  <span className="text-sm text-gray-400">
                    Analyzing with multiple AI models...
                  </span>
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
