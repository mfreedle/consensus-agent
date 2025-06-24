// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
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
  file_path?: string;
  google_drive_id?: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
}

// LLM Model Types
export interface LLMModel {
  id: string;
  provider: 'openai' | 'grok' | 'claude';
  model_name: string;
  display_name: string;
  is_active: boolean;
  capabilities?: Record<string, any>;
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
