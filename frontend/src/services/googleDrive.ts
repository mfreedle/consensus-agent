import { apiService } from './api';

export interface GoogleAuthURL {
  auth_url: string;
  state: string;
}

export interface GoogleTokens {
  access_token: string;
  refresh_token?: string;
  token_expiry?: string;
  scope?: string;
}

export interface GoogleDriveFile {
  id: string;
  name: string;
  type: string;
  mime_type: string;
  modified_time?: string;
  web_view_link?: string;
  owners: any[];
}

export interface GoogleDriveFileList {
  files: GoogleDriveFile[];
  total_count: number;
}

export interface GoogleDriveConnection {
  connected: boolean;
  user_email?: string;
  connection_date?: string;
  scopes: string[];
}

export interface GoogleDocumentContent {
  document_id: string;
  title: string;
  content: string;
  revision_id?: string;
}

export interface GoogleOAuthCallback {
  code: string;
  state: string;
  scope?: string;
}

export interface ListFilesOptions {
  file_type?: string;
  limit?: number;
}

class GoogleDriveService {
  /**
   * Get Google OAuth authorization URL
   */
  async getAuthUrl(token: string): Promise<GoogleAuthURL> {
    const response = await (apiService as any).request('/google/auth');
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Handle OAuth callback and exchange code for tokens
   */
  async handleCallback(token: string, callbackData: GoogleOAuthCallback): Promise<GoogleTokens> {
    const response = await (apiService as any).request('/google/callback', {
      method: 'POST',
      body: JSON.stringify(callbackData)
    });
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Get Google Drive connection status
   */
  async getConnectionStatus(token: string): Promise<GoogleDriveConnection> {
    const response = await (apiService as any).request('/google/connection');
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Disconnect Google Drive
   */
  async disconnect(token: string): Promise<{ message: string }> {
    const response = await (apiService as any).request('/google/disconnect', {
      method: 'DELETE'
    });
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * List Google Drive files
   */
  async listFiles(token: string, options: ListFilesOptions = {}): Promise<GoogleDriveFileList> {
    const params = new URLSearchParams();
    
    if (options.file_type) {
      params.append('file_type', options.file_type);
    }
    if (options.limit) {
      params.append('limit', options.limit.toString());
    }

    const queryString = params.toString();
    const endpoint = queryString ? `/google/files?${queryString}` : '/google/files';
    const response = await (apiService as any).request(endpoint);
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Get Google Document content
   */
  async getDocumentContent(token: string, fileId: string): Promise<GoogleDocumentContent> {
    const response = await (apiService as any).request(`/google/files/${fileId}/content`);
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Edit Google Document (placeholder)
   */
  async editDocument(token: string, fileId: string, content: string): Promise<{ message: string }> {
    const response = await (apiService as any).request(`/google/files/${fileId}/edit`, {
      method: 'POST',
      body: JSON.stringify({ content })
    });
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Handle OAuth popup callback
   * This method sets up a listener for the OAuth popup callback
   */
  setupOAuthListener(): Promise<{ code: string; state: string }> {
    return new Promise((resolve, reject) => {
      const handleMessage = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;
        
        if (event.data.type === 'GOOGLE_OAUTH_SUCCESS') {
          window.removeEventListener('message', handleMessage);
          resolve({
            code: event.data.code,
            state: event.data.state
          });
        } else if (event.data.type === 'GOOGLE_OAUTH_ERROR') {
          window.removeEventListener('message', handleMessage);
          reject(new Error(event.data.error || 'OAuth authorization failed'));
        }
      };

      window.addEventListener('message', handleMessage);

      // Cleanup after 5 minutes
      setTimeout(() => {
        window.removeEventListener('message', handleMessage);
        reject(new Error('OAuth timeout'));
      }, 5 * 60 * 1000);
    });
  }
}

export const googleDriveService = new GoogleDriveService();
