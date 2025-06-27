import React, { useState, useEffect } from "react";
import {
  Cloud,
  CloudOff,
  Link,
  ExternalLink,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { googleDriveService } from "../services/googleDrive";

interface GoogleDriveConnection {
  connected: boolean;
  user_email?: string;
  connection_date?: string;
  scopes: string[];
}

interface GoogleDriveFile {
  id: string;
  name: string;
  type: string;
  mime_type: string;
  modified_time?: string;
  web_view_link?: string;
  owners: any[];
}

export const GoogleDriveIntegration: React.FC = () => {
  const { token } = useAuth();
  const [connection, setConnection] = useState<GoogleDriveConnection | null>(
    null
  );
  const [files, setFiles] = useState<GoogleDriveFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileType, setFileType] = useState<string>("all");

  const checkConnectionStatus = React.useCallback(async () => {
    if (!token) return;

    try {
      const status = await googleDriveService.getConnectionStatus(token);
      setConnection(status);

      if (status.connected) {
        // Load files after connection status is confirmed
        setLoading(true);
        setError(null);

        try {
          const response = await googleDriveService.listFiles(token, {
            file_type: fileType === "all" ? undefined : fileType,
            limit: 50,
          });
          setFiles(response.files);
        } catch (err: any) {
          setError("Failed to load Google Drive files");
          console.error("Google Drive files error:", err);
        } finally {
          setLoading(false);
        }
      }
    } catch (err: any) {
      setError("Failed to check Google Drive connection status");
      console.error("Google Drive connection check error:", err);
    }
  }, [token, fileType]);

  const loadFiles = React.useCallback(async () => {
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await googleDriveService.listFiles(token, {
        file_type: fileType === "all" ? undefined : fileType,
        limit: 50,
      });
      setFiles(response.files);
    } catch (err: any) {
      setError("Failed to load Google Drive files");
      console.error("Google Drive files error:", err);
    } finally {
      setLoading(false);
    }
  }, [token, fileType]);

  useEffect(() => {
    checkConnectionStatus();
  }, [checkConnectionStatus]);

  const connectGoogleDrive = async () => {
    if (!token) return;

    setConnecting(true);
    setError(null);

    try {
      const authData = await googleDriveService.getAuthUrl(token);

      // Open Google OAuth in a popup window
      const popup = window.open(
        authData.auth_url,
        "google-auth",
        "width=500,height=600,scrollbars=yes,resizable=yes"
      );

      // Listen for the OAuth callback
      const handleCallback = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;

        if (event.data.type === "GOOGLE_OAUTH_SUCCESS") {
          popup?.close();
          window.removeEventListener("message", handleCallback);

          // Process the callback
          handleOAuthCallback(event.data.code, event.data.state);
        } else if (event.data.type === "GOOGLE_OAUTH_ERROR") {
          popup?.close();
          window.removeEventListener("message", handleCallback);
          setError("Google OAuth authorization failed");
          setConnecting(false);
        }
      };

      window.addEventListener("message", handleCallback);

      // Check if popup was closed manually
      const checkClosed = setInterval(() => {
        if (popup?.closed) {
          clearInterval(checkClosed);
          window.removeEventListener("message", handleCallback);
          setConnecting(false);
        }
      }, 1000);
    } catch (err: any) {
      setError("Failed to initiate Google Drive connection");
      setConnecting(false);
      console.error("Google Drive auth error:", err);
    }
  };

  const handleOAuthCallback = async (code: string, state: string) => {
    if (!token) return;

    try {
      await googleDriveService.handleCallback(token, { code, state });
      await checkConnectionStatus();
      setConnecting(false);
    } catch (err: any) {
      setError("Failed to complete Google Drive connection");
      setConnecting(false);
      console.error("OAuth callback error:", err);
    }
  };

  const disconnectGoogleDrive = async () => {
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      await googleDriveService.disconnect(token);
      setConnection({ connected: false, scopes: [] });
      setFiles([]);
    } catch (err: any) {
      setError("Failed to disconnect Google Drive");
      console.error("Google Drive disconnect error:", err);
    } finally {
      setLoading(false);
    }
  };

  const openFile = (file: GoogleDriveFile) => {
    if (file.web_view_link) {
      window.open(file.web_view_link, "_blank");
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case "document":
        return "📄";
      case "spreadsheet":
        return "📊";
      case "presentation":
        return "📽️";
      case "folder":
        return "📁";
      default:
        return "📄";
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="google-drive-integration">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {connection?.connected ? (
            <Cloud className="h-6 w-6 text-blue-500" />
          ) : (
            <CloudOff className="h-6 w-6 text-gray-400" />
          )}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Google Drive Integration
          </h3>
        </div>

        {connection?.connected ? (
          <button
            onClick={disconnectGoogleDrive}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin inline mr-2" />
                Disconnecting...
              </>
            ) : (
              "Disconnect"
            )}
          </button>
        ) : (
          <button
            onClick={connectGoogleDrive}
            disabled={connecting}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {connecting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin inline mr-2" />
                Connecting...
              </>
            ) : (
              <>
                <Link className="h-4 w-4 inline mr-2" />
                Connect Google Drive
              </>
            )}
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {connection?.connected ? (
        <div>
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
              <p className="text-sm text-green-700">
                Google Drive connected successfully
              </p>
            </div>
          </div>

          {/* File Type Filter */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Filter by file type:
            </label>
            <select
              value={fileType}
              onChange={(e) => {
                setFileType(e.target.value);
                if (connection.connected) {
                  setTimeout(loadFiles, 100);
                }
              }}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="all">All Files</option>
              <option value="document">Google Docs</option>
              <option value="spreadsheet">Google Sheets</option>
              <option value="presentation">Google Slides</option>
            </select>
          </div>

          {/* File List */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-md font-medium text-gray-900 dark:text-white">
                Your Google Drive Files ({files.length})
              </h4>
              <button
                onClick={loadFiles}
                disabled={loading}
                className="px-3 py-1 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded hover:bg-blue-100 disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  "Refresh"
                )}
              </button>
            </div>

            <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-md dark:border-gray-700">
              {files.length === 0 ? (
                <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                  {loading ? "Loading files..." : "No files found"}
                </div>
              ) : (
                files.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700 last:border-b-0 hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <span className="text-lg">{getFileIcon(file.type)}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Modified: {formatDate(file.modified_time)}
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => openFile(file)}
                      className="ml-2 p-1 text-gray-400 hover:text-blue-500"
                      title="Open in Google Drive"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <CloudOff className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Connect your Google Drive to access and work with your documents
            directly in the chat.
          </p>
          <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1 mb-6">
            <li>• Access Google Docs, Sheets, and Slides</li>
            <li>• Let AI read and analyze your documents</li>
            <li>• Edit documents with AI assistance</li>
          </ul>
        </div>
      )}
    </div>
  );
};
