import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  Send,
  Loader2,
  Bot,
  User,
  Paperclip,
  Mic,
  Sparkles,
  FileText,
  Settings,
  Brain,
} from "lucide-react";
import { useForm } from "react-hook-form";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ConsensusResponse } from "../services/api";
import { enhancedApiService } from "../services/enhancedApi";
import { useErrorHandler } from "../hooks/useErrorHandler";
import { SocketMessage, ModelSelectionState, ProcessingStatus } from "../types";
import ConsensusDebateVisualizer from "./ConsensusDebateVisualizer";
import ConsensusProcessingIndicator from "./ConsensusProcessingIndicator";
import FileUploadModal from "./FileUploadModal";

interface ModernChatInterfaceProps {
  sessionId: string | null;
  onSessionCreated: (sessionId: string) => void;
  socketMessages?: SocketMessage[];
  onSendSocketMessage?: (
    message: string,
    attachedFileIds?: string[],
    useConsensus?: boolean,
    selectedModels?: string[]
  ) => boolean;
  isSocketConnected?: boolean;
  modelSelection?: ModelSelectionState;
  processingStatus?: ProcessingStatus | null;
}

interface AttachedFile {
  id: string;
  file: File;
  uploaded: boolean;
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

const ModernChatInterface: React.FC<ModernChatInterfaceProps> = ({
  sessionId,
  onSessionCreated,
  socketMessages = [],
  onSendSocketMessage,
  isSocketConnected = false,
  modelSelection,
  processingStatus,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [consensusPhase, setConsensusPhase] = useState<
    "analyzing" | "processing" | "consensus" | "finalizing"
  >("processing");
  const [processingMessage, setProcessingMessage] =
    useState<string>("AI is thinking...");

  // Update processing state when status changes
  useEffect(() => {
    if (processingStatus) {
      console.log(
        "🎯 ModernChatInterface: Processing status updated:",
        processingStatus
      );
      setConsensusPhase(processingStatus.status);
      setProcessingMessage(processingStatus.message);
    } else {
      console.log("🎯 ModernChatInterface: Processing status cleared");
    }
  }, [processingStatus]);
  const [fileUploadModal, setFileUploadModal] = useState<{
    isOpen: boolean;
    mode: "attach" | "knowledge";
  }>({ isOpen: false, mode: "attach" });
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { addError } = useErrorHandler();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<MessageForm>();

  const messageValue = watch("message", "");

  // Scroll to bottom function
  const scrollToBottom = useCallback(() => {
    // Use a small delay to ensure the DOM has updated
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "end",
        inline: "nearest",
      });
    }, 100);
  }, []);

  // Load messages for session
  useEffect(() => {
    const loadMessages = async () => {
      if (!sessionId) {
        setMessages([]);
        return;
      }

      try {
        const sessionMessages = await enhancedApiService.getChatMessages(
          parseInt(sessionId)
        );

        const formattedMessages: Message[] = sessionMessages.map((msg) => ({
          id: msg.id,
          role: msg.role as "user" | "assistant" | "system",
          content: msg.content,
          timestamp: msg.created_at,
          session_id: msg.session_id,
          consensus: msg.consensus_data as ConsensusResponse | undefined,
        }));

        setMessages(formattedMessages);
      } catch (error) {
        console.error("Failed to load messages for session:", sessionId, error);
        addError(error, "api", "Failed to load conversation history");
        setMessages([]);
      }
    };

    loadMessages();
  }, [sessionId, addError]);

  // Add socket messages to the regular messages (only for current session)
  useEffect(() => {
    if (socketMessages.length > 0 && sessionId) {
      const currentSessionIdNum = parseInt(sessionId);

      // Filter messages to only include those for the current session
      const sessionMessages = socketMessages.filter((socketMsg) => {
        const msgSessionId =
          typeof socketMsg.session_id === "string"
            ? parseInt(socketMsg.session_id)
            : socketMsg.session_id;
        return msgSessionId === currentSessionIdNum;
      });

      if (sessionMessages.length > 0) {
        const convertedMessages: Message[] = sessionMessages.map(
          (socketMsg, index) => ({
            id: Date.now() + index,
            role: socketMsg.role,
            content: socketMsg.content,
            timestamp: socketMsg.timestamp || new Date().toISOString(),
            session_id: currentSessionIdNum,
            consensus: socketMsg.consensus as ConsensusResponse | undefined,
          })
        );

        setMessages((prev) => {
          const existingContents = prev.map((msg) => msg.content);
          const newMessages = convertedMessages.filter(
            (msg) => !existingContents.includes(msg.content)
          );

          // Turn off loading when we receive an assistant message via Socket.IO
          const hasNewAssistantMessage = newMessages.some(
            (msg) => msg.role === "assistant"
          );
          if (hasNewAssistantMessage && isLoading) {
            setIsLoading(false);
          }

          return [...prev, ...newMessages];
        });
      }
    }
  }, [socketMessages, sessionId, isLoading]);

  // Simulate consensus phases when loading for better UX
  useEffect(() => {
    if (
      isLoading &&
      modelSelection?.selectedModels?.length &&
      modelSelection.selectedModels.length > 1
    ) {
      setConsensusPhase("analyzing");

      const phaseTimer1 = setTimeout(
        () => setConsensusPhase("processing"),
        2000
      );
      const phaseTimer2 = setTimeout(
        () => setConsensusPhase("consensus"),
        5000
      );
      const phaseTimer3 = setTimeout(
        () => setConsensusPhase("finalizing"),
        8000
      );

      return () => {
        clearTimeout(phaseTimer1);
        clearTimeout(phaseTimer2);
        clearTimeout(phaseTimer3);
      };
    }
  }, [isLoading, modelSelection?.selectedModels?.length]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [messageValue]);

  // File upload handlers
  const handleAttachFile = () => {
    setFileUploadModal({ isOpen: true, mode: "attach" });
  };

  const handleUploadToKnowledge = () => {
    setFileUploadModal({ isOpen: true, mode: "knowledge" });
  };

  const handleFileAttached = async (file: File, uploadedFileId?: string) => {
    console.log(
      "ModernChatInterface: handleFileAttached called with file:",
      file.name,
      "uploadedFileId:",
      uploadedFileId
    );
    try {
      let fileId: string;

      if (uploadedFileId) {
        // File was already uploaded by ModernFileUpload
        fileId = uploadedFileId;
        console.log(
          "Using pre-uploaded file:",
          file.name,
          "with ID:",
          uploadedFileId
        );
      } else {
        // Upload the file first to get an ID (fallback for direct calls)
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://localhost:8000/files/upload", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Failed to upload file");
        }

        const result = await response.json();
        fileId = result.id;
        console.log("Uploaded file:", file.name, "with ID:", result.id);
      }

      // Add to attached files with ID
      const attachedFile: AttachedFile = {
        id: fileId,
        file: file,
        uploaded: true,
      };

      setAttachedFiles((prev) => {
        const newAttachedFiles = [...prev, attachedFile];
        console.log("Updated attachedFiles state:", newAttachedFiles);
        return newAttachedFiles;
      });
      console.log("File attached successfully:", file.name, "with ID:", fileId);
    } catch (error) {
      console.error("Error uploading file:", error);
      addError(error, "upload", "Failed to attach file. Please try again.");
    }
  };

  const handleFilesUploaded = (files: any[]) => {
    console.log("Files uploaded to knowledge base:", files);
  };

  const handleCloseFileModal = () => {
    setFileUploadModal({ isOpen: false, mode: "attach" });
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

      // Capture attached file IDs before clearing
      const attachedFileIds = attachedFiles.map((af) => af.id);
      console.log(
        "Attached files before sending:",
        attachedFiles.length,
        "File IDs:",
        attachedFileIds
      );

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      reset();
      // Clear attached files after capturing IDs
      setAttachedFiles([]);

      try {
        // Try to send via Socket.IO first if connected
        if (isSocketConnected && onSendSocketMessage) {
          const useConsensus =
            modelSelection?.selectedModels &&
            modelSelection.selectedModels.length > 1;
          const socketSent = onSendSocketMessage(
            data.message,
            attachedFileIds,
            useConsensus,
            modelSelection?.selectedModels
          );
          if (socketSent) {
            console.log(
              "Message sent via Socket.IO",
              attachedFileIds.length > 0
                ? `with ${attachedFileIds.length} attached files`
                : "",
              `use_consensus: ${useConsensus}, models: ${modelSelection?.selectedModels?.join(
                ", "
              )}`
            );
            // DON'T set loading to false immediately - wait for Socket.IO response
            // setIsLoading(false); // ← REMOVED: This was causing the bug
            return;
          }
        }

        // Use enhanced API service to backend (for file attachments or when Socket.IO fails)
        console.log(
          "Sending message to backend API...",
          attachedFileIds.length > 0
            ? `with ${attachedFileIds.length} attached files`
            : ""
        );

        const apiRequest = {
          message: data.message,
          session_id: sessionId ? parseInt(sessionId) : undefined,
          use_consensus:
            modelSelection?.selectedModels &&
            modelSelection.selectedModels.length > 1,
          selected_models: modelSelection?.selectedModels || ["gpt-4.1"], // Use one of our curated models
          attached_file_ids: attachedFileIds,
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
      attachedFiles,
    ]
  );

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const renderWelcomeScreen = () => (
    <div className="welcome-screen">
      <div className="welcome-content">
        <h1 className="welcome-title">Hello! What can I help you with?</h1>
        <p className="welcome-subtitle">
          Ask me anything and I'll provide insights using multiple AI models
          working together through consensus.
        </p>

        {/* Model Status */}
        {modelSelection && (
          <div className="consensus-indicator">
            <Sparkles className="w-4 h-4 text-primary-cyan" />
            <span>
              {modelSelection.selectedModels.length > 1
                ? `${modelSelection.selectedModels.length} AI models ready for consensus`
                : `${modelSelection.selectedModels.length} AI model ready`}
            </span>
            <div className="consensus-models">
              {modelSelection.selectedModels.slice(0, 3).map((model, index) => (
                <span key={index} className="model-badge">
                  {model.replace("gpt-", "GPT-").replace("claude-", "Claude ")}
                </span>
              ))}
              {modelSelection.selectedModels.length > 3 && (
                <span className="model-badge">
                  +{modelSelection.selectedModels.length - 3}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Suggestion Cards */}
        <div className="suggestion-cards">
          <div
            className="suggestion-card"
            onClick={() => {
              if (textareaRef.current) {
                textareaRef.current.value =
                  "Explain quantum computing in simple terms";
                textareaRef.current.focus();
              }
            }}
          >
            <div className="suggestion-card-title">Explain Complex Topics</div>
            <div className="suggestion-card-description">
              Get clear explanations of difficult concepts using multiple AI
              perspectives
            </div>
          </div>

          <div
            className="suggestion-card"
            onClick={() => {
              if (textareaRef.current) {
                textareaRef.current.value =
                  "Analyze the pros and cons of remote work";
                textareaRef.current.focus();
              }
            }}
          >
            <div className="suggestion-card-title">
              Multi-Perspective Analysis
            </div>
            <div className="suggestion-card-description">
              Compare different viewpoints and get balanced consensus insights
            </div>
          </div>

          <div
            className="suggestion-card"
            onClick={() => {
              if (textareaRef.current) {
                textareaRef.current.value =
                  "Help me plan a marketing strategy for a tech startup";
                textareaRef.current.focus();
              }
            }}
          >
            <div className="suggestion-card-title">Strategic Planning</div>
            <div className="suggestion-card-description">
              Get comprehensive strategies validated by multiple AI models
            </div>
          </div>

          <div
            className="suggestion-card"
            onClick={() => {
              if (textareaRef.current) {
                textareaRef.current.value =
                  "Review and improve this code snippet";
                textareaRef.current.focus();
              }
            }}
          >
            <div className="suggestion-card-title">Code Review</div>
            <div className="suggestion-card-description">
              Improve your code with insights from multiple AI programming
              experts
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMessage = (message: Message) => (
    <div key={message.id} className={`message-bubble ${message.role}`}>
      {/* Consensus Indicator for multi-model responses */}
      {message.role === "assistant" &&
        message.consensus &&
        modelSelection?.selectedModels &&
        modelSelection.selectedModels.length > 1 && (
          <div className="consensus-indicator">
            <Brain className="w-4 h-4 text-primary-teal" />
            <span>
              Consensus from {modelSelection.selectedModels.length} models
            </span>
            <div className="consensus-models">
              {modelSelection.selectedModels.slice(0, 3).map((model, index) => (
                <span key={index} className="model-badge">
                  {model.replace("gpt-", "GPT-").replace("claude-", "Claude ")}
                </span>
              ))}
            </div>
          </div>
        )}

      <div className={`message-content ${message.role}`}>
        <div className={`message-avatar ${message.role}`}>
          {message.role === "user" ? (
            <User className="w-4 h-4" />
          ) : (
            <Bot className="w-4 h-4" />
          )}
        </div>

        <div className="message-text">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Enhanced paragraph handling
              p: ({ children, ...props }) => {
                return <p {...props}>{children}</p>;
              },

              // Enhanced heading components
              h1: ({ children }) => <h1>{children}</h1>,
              h2: ({ children }) => <h2>{children}</h2>,
              h3: ({ children }) => <h3>{children}</h3>,
              h4: ({ children }) => <h4>{children}</h4>,
              h5: ({ children }) => <h5>{children}</h5>,
              h6: ({ children }) => <h6>{children}</h6>,

              // Enhanced list components
              ul: ({ children }) => <ul>{children}</ul>,
              ol: ({ children }) => <ol>{children}</ol>,
              li: ({ children }) => <li>{children}</li>,

              // Enhanced code handling with syntax highlighting support
              code: ({ children, className, ...props }) => {
                const isBlock = className?.includes("language-");

                if (isBlock) {
                  return (
                    <pre className="code-block">
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                  );
                } else {
                  return (
                    <code className="inline-code" {...props}>
                      {children}
                    </code>
                  );
                }
              },

              // Enhanced blockquote styling
              blockquote: ({ children }) => <blockquote>{children}</blockquote>,

              // Enhanced text formatting
              strong: ({ children }) => <strong>{children}</strong>,
              em: ({ children }) => <em>{children}</em>,

              // Enhanced link handling
              a: ({ children, href, ...props }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  {...props}
                >
                  {children}
                </a>
              ),

              // Enhanced table components
              table: ({ children }) => (
                <div className="table-container">
                  <table>{children}</table>
                </div>
              ),
              thead: ({ children }) => <thead>{children}</thead>,
              tbody: ({ children }) => <tbody>{children}</tbody>,
              tr: ({ children }) => <tr>{children}</tr>,
              th: ({ children }) => <th>{children}</th>,
              td: ({ children }) => <td>{children}</td>,

              // Enhanced horizontal rule
              hr: () => <hr />,
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>

      <div className="message-timestamp">{formatTime(message.timestamp)}</div>

      {/* Consensus Details */}
      {message.consensus && modelSelection?.showDebateProcess && (
        <div className="mt-4 w-full">
          <ConsensusDebateVisualizer
            consensusData={message.consensus}
            isDebating={false}
            className="w-full"
          />
        </div>
      )}
    </div>
  );

  const renderTypingIndicator = () => {
    console.log(
      "🔍 Rendering typing indicator - isLoading:",
      isLoading,
      "processingStatus:",
      !!processingStatus
    );
    console.log(
      "🔍 Processing message:",
      processingMessage,
      "Phase:",
      consensusPhase
    );

    // Use enhanced consensus indicator for multi-model scenarios
    const isConsensusMode =
      modelSelection?.selectedModels?.length &&
      modelSelection.selectedModels.length > 1;

    if (isConsensusMode) {
      return (
        <div className="message-bubble assistant">
          <div className="message-avatar assistant">
            <Bot className="w-4 h-4" />
          </div>
          <div className="message-content">
            <ConsensusProcessingIndicator
              message={processingMessage}
              phase={consensusPhase}
            />
          </div>
        </div>
      );
    }

    // Standard typing indicator for single model
    return (
      <div className="typing-indicator">
        <div className={`message-avatar assistant`}>
          <Bot className="w-4 h-4" />
        </div>
        <div className="typing-dots">
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
        </div>
        <span className="text-text-muted text-sm ml-2">
          {processingMessage}
        </span>
      </div>
    );
  };

  return (
    <div className="modern-chat-container">
      {/* Messages Area */}
      <div className="modern-chat-messages">
        <div className="messages-container">
          {messages.length === 0 && !sessionId ? (
            renderWelcomeScreen()
          ) : (
            <>
              {messages.map(renderMessage)}
              {(isLoading || processingStatus) && renderTypingIndicator()}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="modern-input-area">
        <div className="modern-input-container">
          {/* Bottom Toolbar */}
          <div className="bottom-toolbar">
            <button
              className="toolbar-button"
              title="Attach file"
              onClick={handleAttachFile}
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <button className="toolbar-button" title="Voice input">
              <Mic className="w-5 h-5" />
            </button>
            <button
              className="toolbar-button"
              title="Document upload"
              onClick={handleUploadToKnowledge}
            >
              <FileText className="w-5 h-5" />
            </button>
            <button className="toolbar-button" title="Settings">
              <Settings className="w-5 h-5" />
            </button>
            <div className="flex-1"></div>
            {!isSocketConnected && (
              <div className="flex items-center space-x-2 text-xs text-amber-400">
                <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></div>
                <span className="hidden sm:inline">HTTP mode</span>
              </div>
            )}
          </div>

          {/* Attached Files Display - Moved above input */}
          {attachedFiles.length > 0 && (
            <div className="attached-files">
              <div className="attached-files-label">
                Attached files ({attachedFiles.length}):
              </div>
              <div className="attached-files-list">
                {attachedFiles.map((attachedFile, index) => (
                  <div key={index} className="attached-file-item">
                    <Paperclip className="w-4 h-4 text-primary-cyan" />
                    <span className="attached-file-name">
                      {attachedFile.file.name}
                    </span>
                    <button
                      onClick={() =>
                        setAttachedFiles((prev) =>
                          prev.filter((_, i) => i !== index)
                        )
                      }
                      className="remove-attached-file"
                      aria-label={`Remove ${attachedFile.file.name}`}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Input Field */}
          <form onSubmit={handleSubmit(onSubmit)} className="relative">
            <div className="modern-input-field">
              <textarea
                {...register("message", { required: "Message is required" })}
                ref={(e) => {
                  register("message").ref(e);
                  textareaRef.current = e;
                }}
                placeholder="Message Consensus Agent..."
                className="modern-textarea"
                disabled={isLoading}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(onSubmit)();
                  }
                }}
              />

              <button
                type="submit"
                disabled={isLoading || !messageValue?.trim()}
                className="modern-send-button"
                aria-label="Send message"
                onClick={(e) => {
                  console.log("Send button clicked!", {
                    isLoading,
                    messageValue,
                    hasMessage: !!messageValue?.trim(),
                    disabled: isLoading || !messageValue?.trim(),
                  });
                }}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>

            {errors.message && (
              <p className="text-red-400 text-xs mt-2 px-2">
                {typeof errors.message === "string"
                  ? errors.message
                  : errors.message.message || "Message is required"}
              </p>
            )}
          </form>
        </div>
      </div>

      {/* File Upload Modal */}
      <FileUploadModal
        isOpen={fileUploadModal.isOpen}
        mode={fileUploadModal.mode}
        onClose={handleCloseFileModal}
        onFileAttached={handleFileAttached}
        onFilesUploaded={handleFilesUploaded}
      />
    </div>
  );
};

export default ModernChatInterface;
