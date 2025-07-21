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
    apiService.setToken(token);
    const response = await apiService.getGoogleAuthUrl();
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Handle OAuth callback and exchange code for tokens
   */
  async handleCallback(token: string, callbackData: GoogleOAuthCallback): Promise<GoogleTokens> {
    apiService.setToken(token);
    const response = await apiService.handleGoogleCallback(callbackData);
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Get Google Drive connection status
   */
  async getConnectionStatus(token: string): Promise<GoogleDriveConnection> {
    apiService.setToken(token);
    const response = await apiService.getGoogleConnectionStatus();
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Disconnect Google Drive
   */
  async disconnect(token: string): Promise<{ message: string }> {
    apiService.setToken(token);
    const response = await apiService.disconnectGoogle();
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * List Google Drive files
   */
  async listFiles(token: string, options: ListFilesOptions = {}): Promise<GoogleDriveFileList> {
    apiService.setToken(token);
    const response = await apiService.getGoogleFiles(options);
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Create a new Google Document
   */
  async createDocument(token: string, title: string, content: string = "", folderId?: string): Promise<any> {
    apiService.setToken(token);
    const response = await apiService.createGoogleDocument({
      title,
      content,
      folder_id: folderId
    });
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Create a new Google Spreadsheet
   */
  async createSpreadsheet(token: string, title: string, folderId?: string): Promise<any> {
    apiService.setToken(token);
    const response = await apiService.createGoogleSpreadsheet({
      title,
      folder_id: folderId
    });
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Create a new Google Presentation
   */
  async createPresentation(token: string, title: string, folderId?: string): Promise<any> {
    apiService.setToken(token);
    const response = await apiService.createGooglePresentation({
      title,
      folder_id: folderId
    });
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Edit file content
   */
  async editFile(token: string, fileId: string, content: string): Promise<any> {
    apiService.setToken(token);
    const response = await apiService.editGoogleFile(fileId, { content });
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Get file content
   */
  async getFileContent(token: string, fileId: string): Promise<GoogleDocumentContent> {
    apiService.setToken(token);
    const response = await apiService.getGoogleFileContent(fileId);
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
  }

  /**
   * Search files in Google Drive
   */
  async searchFiles(token: string, searchQuery: string, options: {
    file_type?: string;
    limit?: number;
  } = {}): Promise<GoogleDriveFileList> {
    apiService.setToken(token);
    const response = await apiService.searchGoogleFiles(searchQuery, options);
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data!;
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
