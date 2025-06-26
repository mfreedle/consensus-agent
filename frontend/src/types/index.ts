// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Socket.IO Types
export interface SocketMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  session_id: number | string;
  timestamp?: string;
  consensus?: ConsensusData;
}

export interface SocketError {
  error: string;
}

export interface SocketJoinData {
  session_id: string;
}

export interface SocketSendMessageData {
  session_id: string;
  message: string;
  token: string;
}

// User Types
export interface User {
  id: string;
  username: string;
  created_at: string;
  google_drive_token?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

// Chat Types
export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model_used?: string;
  consensus_data?: ConsensusData;
  created_at: string;
}

export interface ConsensusData {
  openai_response?: {
    content: string;
    confidence: number;
    reasoning: string;
  };
  grok_response?: {
    content: string;
    confidence: number;
    reasoning: string;
  };
  final_consensus: string;
  confidence_score: number;
  reasoning: string;
  debate_points?: string[];
}

export interface SendMessageRequest {
  session_id?: string;
  content: string;
}

export interface SendMessageResponse {
  message: Message;
  session_id: string;
}

// File Types
export interface FileUpload {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  file_path?: string;
  google_drive_id?: string;
  google_drive_url?: string;
  file_type: string;
  file_size: number;
  mime_type?: string;
  is_processed: boolean;
  processing_error?: string;
  uploaded_at: string;
  updated_at?: string;
}

export interface FileUploadRequest {
  file: File;
}

export interface FileUploadResponse {
  message: string;
  filename: string;
  size: number;
  file_id?: string;
}

export interface FileListResponse {
  files: FileUpload[];
}

export interface SupportedFileType {
  extension: string;
  mimeType: string;
  maxSize: number; // in MB
  category: 'document' | 'spreadsheet' | 'presentation' | 'image' | 'other';
}

export const SUPPORTED_FILE_TYPES: SupportedFileType[] = [
  // Documents
  { extension: '.pdf', mimeType: 'application/pdf', maxSize: 50, category: 'document' },
  { extension: '.docx', mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', maxSize: 50, category: 'document' },
  { extension: '.txt', mimeType: 'text/plain', maxSize: 10, category: 'document' },
  { extension: '.md', mimeType: 'text/markdown', maxSize: 10, category: 'document' },
  
  // Spreadsheets
  { extension: '.xlsx', mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', maxSize: 50, category: 'spreadsheet' },
  { extension: '.csv', mimeType: 'text/csv', maxSize: 10, category: 'spreadsheet' },
  
  // Presentations
  { extension: '.pptx', mimeType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation', maxSize: 100, category: 'presentation' },
];

// LLM Model Types
export interface LLMModel {
  id: string;
  provider: 'openai' | 'grok' | 'claude';
  model_name?: string;
  display_name: string;
  description?: string;
  is_active?: boolean;
  supports_streaming?: boolean;
  supports_function_calling?: boolean;
  capabilities?: Record<string, any>;
  created_at?: string;
}

export interface ModelSelectionState {
  selectedModels: string[];
  debateMode: 'consensus' | 'detailed' | 'quick';
  showDebateProcess: boolean;
}

export interface DebateStep {
  id: string;
  step_number: number;
  model_id: string;
  model_name: string;
  content: string;
  confidence: number;
  reasoning: string;
  timestamp: string;
}

export interface ConsensusDebate {
  id: string;
  session_id: string;
  user_message: string;
  selected_models: string[];
  debate_steps: DebateStep[];
  final_consensus: string;
  confidence_score: number;
  reasoning: string;
  debate_points: string[];
  created_at: string;
}

// WebSocket Types
export interface WebSocketMessage {
  type: 'typing' | 'message' | 'error' | 'status';
  data: any;
  session_id?: string;
}

// UI State Types
export interface UIState {
  isAuthenticated: boolean;
  currentUser: User | null;
  isSidebarOpen: boolean;
  currentSessionId: string | null;
  isLoading: boolean;
  error: string | null;
}
