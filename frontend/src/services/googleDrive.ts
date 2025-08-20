import { apiService } from "./api";

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
    const response = await (apiService as any).request("/api/google/auth");
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Handle OAuth callback and exchange code for tokens
   */
  async handleCallback(
    token: string,
    callbackData: GoogleOAuthCallback
  ): Promise<GoogleTokens> {
    apiService.setToken(token);
    const response = await (apiService as any).request("/api/google/callback", {
      method: "POST",
      body: JSON.stringify(callbackData),
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
    apiService.setToken(token);
    const response = await (apiService as any).request(
      "/api/google/connection"
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Disconnect Google Drive
   */
  async disconnect(token: string): Promise<{ message: string }> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      "/api/google/disconnect",
      {
        method: "DELETE",
      }
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * List Google Drive files
   */
  async listFiles(
    token: string,
    options: ListFilesOptions = {}
  ): Promise<GoogleDriveFileList> {
    apiService.setToken(token);
    const params = new URLSearchParams();

    if (options.file_type) {
      params.append("file_type", options.file_type);
    }
    if (options.limit) {
      params.append("limit", options.limit.toString());
    }

    const queryString = params.toString();
    const endpoint = queryString
      ? `/api/google/files?${queryString}`
      : "/api/google/files";
    const response = await (apiService as any).request(endpoint);
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Search files in Google Drive
   */
  async searchFiles(
    token: string,
    searchQuery: string,
    options: {
      file_type?: string;
      limit?: number;
    } = {}
  ): Promise<GoogleDriveFileList> {
    apiService.setToken(token);
    const params = new URLSearchParams();
    params.append("q", searchQuery);
    if (options.file_type) params.append("file_type", options.file_type);
    if (options.limit) params.append("limit", options.limit.toString());

    const response = await (apiService as any).request(
      `/api/google/files/search?${params.toString()}`
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * List contents of a specific folder
   */
  async listFolderContents(
    token: string,
    folderId: string,
    options: {
      file_type?: string;
      limit?: number;
    } = {}
  ): Promise<GoogleDriveFileList> {
    apiService.setToken(token);
    const params = new URLSearchParams();
    if (options.file_type) params.append("file_type", options.file_type);
    if (options.limit) params.append("limit", options.limit.toString());

    const response = await (apiService as any).request(
      `/api/google/folders/${folderId}/contents?${params.toString()}`
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Find a folder by name
   */
  async findFolderByName(
    token: string,
    folderName: string
  ): Promise<GoogleDriveFile> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      `/api/google/folders/find/${encodeURIComponent(folderName)}`
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * List all files with their full paths
   */
  async listFilesWithPaths(
    token: string,
    options: {
      file_type?: string;
      limit?: number;
    } = {}
  ): Promise<GoogleDriveFileList> {
    apiService.setToken(token);
    const params = new URLSearchParams();
    if (options.file_type) params.append("file_type", options.file_type);
    if (options.limit) params.append("limit", options.limit.toString());

    const response = await (apiService as any).request(
      `/api/google/files/with-paths?${params.toString()}`
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Get Google Document content
   */
  async getDocumentContent(
    token: string,
    fileId: string
  ): Promise<GoogleDocumentContent> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      `/api/google/files/${fileId}/content`
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Edit Google Document (placeholder)
   */
  async editDocument(
    token: string,
    fileId: string,
    content: string
  ): Promise<{ message: string }> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      `/api/google/files/${fileId}/edit`,
      {
        method: "POST",
        body: JSON.stringify({ content }),
      }
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Create a new Google Document
   */
  async createDocument(
    token: string,
    title: string,
    content: string
  ): Promise<{ file_id: string; web_view_link: string; message: string }> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      "/api/google/documents/create",
      {
        method: "POST",
        body: JSON.stringify({ title, content }),
      }
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Create a new Google Spreadsheet
   */
  async createSpreadsheet(
    token: string,
    title: string
  ): Promise<{ file_id: string; web_view_link: string; message: string }> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      "/api/google/spreadsheets/create",
      {
        method: "POST",
        body: JSON.stringify({ title }),
      }
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Create a new Google Slides presentation
   */
  async createPresentation(
    token: string,
    title: string
  ): Promise<{ file_id: string; web_view_link: string; message: string }> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      "/api/google/presentations/create",
      {
        method: "POST",
        body: JSON.stringify({ title }),
      }
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Edit Google Spreadsheet
   */
  async editSpreadsheet(
    token: string,
    fileId: string,
    sheetName: string,
    rangeName: string,
    values: string[][]
  ): Promise<{ message: string }> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      `/api/google/spreadsheets/${fileId}/edit`,
      {
        method: "POST",
        body: JSON.stringify({
          sheet_name: sheetName,
          range_name: rangeName,
          values,
        }),
      }
    );
    if (response.error) {
      throw new Error(response.error);
    }
    return response.data;
  }

  /**
   * Add slide to Google Presentation
   */
  async addSlideToPresentation(
    token: string,
    fileId: string,
    title: string,
    content: string
  ): Promise<{ message: string }> {
    apiService.setToken(token);
    const response = await (apiService as any).request(
      `/api/google/presentations/${fileId}/slides/add`,
      {
        method: "POST",
        body: JSON.stringify({ title, content }),
      }
    );
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

        if (event.data.type === "GOOGLE_OAUTH_SUCCESS") {
          window.removeEventListener("message", handleMessage);
          resolve({
            code: event.data.code,
            state: event.data.state,
          });
        } else if (event.data.type === "GOOGLE_OAUTH_ERROR") {
          window.removeEventListener("message", handleMessage);
          reject(new Error(event.data.error || "OAuth authorization failed"));
        }
      };

      window.addEventListener("message", handleMessage);

      // Cleanup after 5 minutes
      setTimeout(() => {
        window.removeEventListener("message", handleMessage);
        reject(new Error("OAuth timeout"));
      }, 5 * 60 * 1000);
    });
  }
}

export const googleDriveService = new GoogleDriveService();
