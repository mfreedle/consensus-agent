export interface ApiRequestOptions extends RequestInit {
  timeout?: number;
  retries?: number;
}

export interface ApiError extends Error {
  status?: number;
  code?: string;
  details?: any;
  type: 'network' | 'validation' | 'auth' | 'upload' | 'api' | 'unknown';
}

export interface SendMessageRequest {
  message: string;
  session_id?: number;
  use_consensus?: boolean;
  selected_models?: string[];
  attached_file_ids?: string[];
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

// Enhanced API service with better error handling
export class EnhancedApiService {
  private token: string | null = null;
  private baseURL: string;
  private defaultTimeout: number = 30000; // 30 seconds

  constructor(baseURL: string = process.env.REACT_APP_API_URL || 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  private async requestWithTimeout(
    url: string, 
    options: RequestInit, 
    timeout: number
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw this.createApiError(
          'Request timeout - please try again',
          'network',
          { timeout, url }
        );
      }
      throw error;
    }
  }

  private createApiError(
    message: string,
    type: 'network' | 'validation' | 'auth' | 'upload' | 'api' | 'unknown',
    details?: any,
    status?: number
  ): ApiError {
    const error = new Error(message) as ApiError;
    error.type = type;
    error.status = status;
    error.details = details;
    return error;
  }

  private async handleResponse<T>(response: Response, endpoint: string): Promise<T> {
    let data: any;

    try {
      const text = await response.text();
      data = text ? JSON.parse(text) : {};
    } catch (parseError) {        throw this.createApiError(
          'Invalid response format from server',
          'api',
          { endpoint, parseError },
          response.status
        );
    }

    if (!response.ok) {
      // Handle specific HTTP status codes
      switch (response.status) {
        case 401:
          this.clearToken(); // Clear invalid token
          throw this.createApiError(
            'Authentication required - please log in again',
            'auth',
            data,
            401
          );
        
        case 403:
          throw this.createApiError(
            'Access denied - insufficient permissions',
            'auth',
            data,
            403
          );
        
        case 404:
          throw this.createApiError(
            'Resource not found',
            'api',
            data,
            404
          );
        
        case 422:
          // Handle validation errors
          if (data.detail && Array.isArray(data.detail)) {
            const validationErrors = data.detail.map((err: any) => 
              `${err.loc?.join('.') || 'field'}: ${err.msg}`
            ).join(', ');
            throw this.createApiError(
              `Validation failed: ${validationErrors}`,
              'validation',
              data,
              422
            );
          }
          break;
        
        case 429:
          throw this.createApiError(
            'Too many requests - please wait before trying again',
            'api',
            data,
            429
          );
        
        case 500:
        case 502:
        case 503:
          throw this.createApiError(
            'Server error - please try again later',
            'api',
            data,
            response.status
          );
      }

      // Generic error handling
      const errorMessage = data.detail || data.message || data.error || 'An unexpected error occurred';
      throw this.createApiError(
        errorMessage,
        'api',
        data,
        response.status
      );
    }

    return data;
  }

  async request<T>(
    endpoint: string,
    options: ApiRequestOptions = {}
  ): Promise<T> {
    const {
      timeout = this.defaultTimeout,
      retries = 1,
      ...fetchOptions
    } = options;

    const url = `${this.baseURL}${endpoint}`;
    
    const headers: Record<string, string> = {
      ...(fetchOptions.headers as Record<string, string>),
    };

    // Only set Content-Type for JSON, let browser set it for FormData
    if (!(fetchOptions.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const finalOptions: RequestInit = {
      ...fetchOptions,
      headers,
    };

    let lastError: any;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await this.requestWithTimeout(url, finalOptions, timeout);
        return await this.handleResponse<T>(response, endpoint);
      } catch (error) {
        lastError = error;
        
        // Don't retry on certain errors
        if (error instanceof Error && (error as ApiError).type === 'auth') {
          break;
        }
        if (error instanceof Error && (error as ApiError).type === 'validation') {
          break;
        }
        if (error instanceof Error && (error as ApiError).status === 404) {
          break;
        }

        // If this is the last attempt, don't wait
        if (attempt === retries) {
          break;
        }

        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, attempt), 5000);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    // Handle network errors
    if (lastError instanceof Error && lastError.name === 'TypeError') {
      throw this.createApiError(
        'Network error - please check your connection',
        'network',
        { originalError: lastError.message, endpoint }
      );
    }

    throw lastError;
  }

  // Safe wrapper that catches errors and returns ApiResponse format
  async safeRequest<T>(
    endpoint: string,
    options: ApiRequestOptions = {}
  ): Promise<{ data?: T; error?: string }> {
    try {
      const data = await this.request<T>(endpoint, options);
      return { data };
    } catch (error) {
      if (error instanceof Error) {
        return { error: error.message };
      }
      return { error: 'An unexpected error occurred' };
    }
  }

  // Chat methods
  async sendMessage(request: SendMessageRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat/message', {
      method: 'POST',
      body: JSON.stringify(request),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async getChatMessages(sessionId: number): Promise<ChatResponseMessage[]> {
    return this.request<ChatResponseMessage[]>(`/chat/sessions/${sessionId}/messages`, {
      method: 'GET',
    });
  }

  async deleteChatSession(sessionId: number): Promise<{message: string}> {
    return this.request<{message: string}>(`/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // Model management methods  
  async getAvailableModels(): Promise<any[]> {
    return this.request<any[]>('/api/models', {
      method: 'GET',
    });
  }

  // File management methods
  async getUserFiles(): Promise<{files: any[]}> {
    return this.request<{files: any[]}>('/files', {
      method: 'GET',
    });
  }

  async deleteFile(fileId: string): Promise<any> {
    return this.request<any>(`/files/${fileId}`, {
      method: 'DELETE',
    });
  }

  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    // For file uploads, we need a custom implementation with progress tracking
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = (event.loaded / event.total) * 100;
            onProgress(progress);
          }
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            resolve(xhr.responseText);
          }
        } else {
          const error: ApiError = new Error(`HTTP ${xhr.status}: ${xhr.statusText}`) as ApiError;
          error.status = xhr.status;
          error.type = xhr.status >= 500 ? 'api' : 'validation';
          reject(error);
        }
      });

      xhr.addEventListener('error', () => {
        const error: ApiError = new Error('Network error during file upload') as ApiError;
        error.type = 'network';
        reject(error);
      });

      xhr.addEventListener('timeout', () => {
        const error: ApiError = new Error('File upload timed out') as ApiError;
        error.type = 'network';
        reject(error);
      });

      xhr.open('POST', `${this.baseURL}/files/upload`);
      
      if (this.token) {
        xhr.setRequestHeader('Authorization', `Bearer ${this.token}`);
      }

      xhr.timeout = 300000; // 5 minutes for file uploads
      xhr.send(formData);
    });
  }
}

// Create singleton instance
export const enhancedApiService = new EnhancedApiService();
