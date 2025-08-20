// Get base URL and ensure we don't double the /api prefix
const getApiBaseUrl = () => {
  const envUrl = process.env.REACT_APP_API_URL;
  if (envUrl) {
    return envUrl;
  }
  // In production, use empty string as base URL since our endpoints already include /api
  // In development use localhost
  return process.env.NODE_ENV === "production" ? "" : "http://localhost:8000";
};

const API_BASE_URL = getApiBaseUrl();

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email?: string;
  password: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface ProfileUpdateRequest {
  email?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: {
    id: number;
    username: string;
    email?: string;
  };
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ChatSession {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  content: string;
  role: "user" | "assistant";
  timestamp: string;
  session_id: number;
}

export interface SendMessageRequest {
  message: string;
  session_id?: number;
  use_consensus?: boolean;
  selected_models?: string[];
}

export interface ChatResponseMessage {
  id: number;
  content: string;
  role: string;
  session_id: number;
  model_used?: string;
  consensus_data?: any;
  created_at: string;
}

export interface ChatResponseSession {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at?: string;
}

export interface ChatResponse {
  message: ChatResponseMessage;
  session: ChatResponseSession;
}

export interface ConsensusResponse {
  openai_response: {
    content: string;
    confidence: number;
    reasoning: string;
  };
  grok_response: {
    content: string;
    confidence: number;
    reasoning: string;
  };
  final_consensus: string;
  confidence_score: number;
  reasoning: string;
  debate_points: string[];
}

class ApiService {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage on initialization
    this.token = localStorage.getItem("auth_token");
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem("auth_token", token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem("auth_token");
  }
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    // Only set Content-Type for JSON, let browser set it for FormData
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    // Ensure token is loaded from localStorage if not in memory
    if (!this.token) {
      this.token = localStorage.getItem("auth_token");
    }

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle FastAPI validation errors
        if (data.detail && Array.isArray(data.detail)) {
          const errorMessage = data.detail
            .map((err: any) => err.msg)
            .join(", ");
          return { error: errorMessage };
        }
        return {
          error: data.detail || data.message || "An error occurred",
        };
      }

      return { data };
    } catch (error) {
      return {
        error: "Network error. Please check your connection.",
      };
    }
  } // Authentication endpoints
  async login(credentials: LoginRequest): Promise<ApiResponse<TokenResponse>> {
    return this.request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  }

  async register(
    userData: RegisterRequest
  ): Promise<ApiResponse<AuthResponse>> {
    return this.request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<ApiResponse<any>> {
    return this.request<any>("/api/auth/me");
  }

  async changePassword(
    passwordData: PasswordChangeRequest
  ): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>("/api/auth/change-password", {
      method: "PUT",
      body: JSON.stringify(passwordData),
    });
  }

  async updateProfile(
    profileData: ProfileUpdateRequest
  ): Promise<ApiResponse<any>> {
    return this.request<any>("/api/auth/profile", {
      method: "PUT",
      body: JSON.stringify(profileData),
    });
  }

  // Chat endpoints
  async getChatSessions(): Promise<ApiResponse<ChatSession[]>> {
    return this.request<ChatSession[]>("/api/chat/sessions");
  }

  async createChatSession(title?: string): Promise<ApiResponse<ChatSession>> {
    return this.request<ChatSession>("/api/chat/sessions", {
      method: "POST",
      body: JSON.stringify({ title: title || "New Chat" }),
    });
  }

  async getChatMessages(
    sessionId: number
  ): Promise<ApiResponse<ChatMessage[]>> {
    return this.request<ChatMessage[]>(
      `/api/chat/sessions/${sessionId}/messages`
    );
  }

  async deleteChatSession(
    sessionId: number
  ): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(
      `/api/chat/sessions/${sessionId}`,
      {
        method: "DELETE",
      }
    );
  }

  async sendMessage(
    request: SendMessageRequest
  ): Promise<ApiResponse<ChatResponse>> {
    return this.request<ChatResponse>("/api/chat/message", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // Models endpoints
  async getAvailableModels(): Promise<ApiResponse<any[]>> {
    return this.request<any[]>("/api/models");
  }

  // Files endpoints  // File management endpoints
  async uploadFile(file: File): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append("file", file);

    return this.request<any>("/api/files/upload", {
      method: "POST",
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    });
  }
  async getUserFiles(): Promise<ApiResponse<{ files: any[] }>> {
    return this.request<{ files: any[] }>("/api/files/");
  }

  async deleteFile(fileId: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/api/files/${fileId}`, {
      method: "DELETE",
    });
  }

  async getFileContent(fileId: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/api/files/${fileId}/content`);
  }

  async updateFile(fileId: string, data: any): Promise<ApiResponse<any>> {
    return this.request<any>(`/api/files/${fileId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }
}

export const apiService = new ApiService();
