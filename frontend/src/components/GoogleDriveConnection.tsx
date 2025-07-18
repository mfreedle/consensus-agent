import React, { useState, useEffect, useCallback } from "react";
import { ExternalLink, CheckCircle, AlertCircle, Settings } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { googleDriveService } from "../services/googleDrive";
import type { GoogleDriveConnection as GoogleDriveConnectionType } from "../services/googleDrive";

interface GoogleDriveConnectionProps {
  onConnectionChange?: (connected: boolean) => void;
}

export const GoogleDriveConnectionWidget: React.FC<
  GoogleDriveConnectionProps
> = ({ onConnectionChange }) => {
  const { token } = useAuth();
  const [connectionStatus, setConnectionStatus] =
    useState<GoogleDriveConnectionType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkConnectionStatus = useCallback(async () => {
    if (!token) return;

    try {
      setLoading(true);
      const status = await googleDriveService.getConnectionStatus(token);
      setConnectionStatus(status);
      onConnectionChange?.(status.connected);
    } catch (err: any) {
      setError(`Failed to check connection: ${err.message}`);
      setConnectionStatus({ connected: false, scopes: [] });
    } finally {
      setLoading(false);
    }
  }, [token, onConnectionChange]);

  useEffect(() => {
    if (token) {
      checkConnectionStatus();
    }
  }, [token, checkConnectionStatus]);

  const handleConnect = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);

      // Get auth URL
      const authData = await googleDriveService.getAuthUrl(token);

      // Set up OAuth listener
      const callbackPromise = googleDriveService.setupOAuthListener();

      // Open popup
      const popup = window.open(
        authData.auth_url,
        "google-oauth",
        "width=500,height=600,scrollbars=yes,resizable=yes"
      );

      if (!popup) {
        throw new Error(
          "Failed to open OAuth popup. Please allow popups for this site."
        );
      }

      // Wait for callback
      const callbackData = await callbackPromise;

      // Handle the callback
      await googleDriveService.handleCallback(token, callbackData);

      // Refresh connection status
      await checkConnectionStatus();

      popup.close();
    } catch (err: any) {
      setError(`Connection failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!token || !connectionStatus?.connected) return;

    if (
      !window.confirm(
        "Are you sure you want to disconnect your Google Drive account?"
      )
    ) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await googleDriveService.disconnect(token);
      await checkConnectionStatus();
    } catch (err: any) {
      setError(`Disconnection failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !connectionStatus) {
    return (
      <div className="google-drive-connection">
        <div className="flex items-center space-x-2 text-gray-500">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          <span className="text-sm">Checking Google Drive connection...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="google-drive-connection">
      {error && (
        <div className="alert alert-error mb-3">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {connectionStatus?.connected ? (
            <>
              <CheckCircle className="h-4 w-4 text-green-500" />
              <div className="text-sm">
                <div className="font-medium text-gray-900 dark:text-white">
                  Google Drive Connected
                </div>
                {connectionStatus.user_email && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {connectionStatus.user_email}
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <AlertCircle className="h-4 w-4 text-gray-400" />
              <div className="text-sm">
                <div className="font-medium text-gray-900 dark:text-white">
                  Google Drive Not Connected
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Connect to enable LLM file operations
                </div>
              </div>
            </>
          )}
        </div>

        <div className="flex space-x-2">
          {connectionStatus?.connected ? (
            <button
              onClick={handleDisconnect}
              disabled={loading}
              className="flex items-center space-x-1 px-3 py-1 text-xs bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50 transition-colors"
            >
              <Settings className="h-3 w-3" />
              <span>Disconnect</span>
            </button>
          ) : (
            <button
              onClick={() => {
                if (!token) {
                  setError("You must be logged in to connect Google Drive.");
                  return;
                }
                handleConnect();
              }}
              disabled={loading}
              className="flex items-center space-x-1 px-3 py-1 text-xs bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 transition-colors"
            >
              <ExternalLink className="h-3 w-3" />
              <span>Connect</span>
            </button>
          )}
        </div>
      </div>

      {connectionStatus?.connected && connectionStatus.scopes.length > 0 && (
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          <div className="font-medium">Permissions:</div>
          <div className="flex flex-wrap gap-1 mt-1">
            {connectionStatus.scopes.map((scope) => (
              <span
                key={scope}
                className="inline-block px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs"
              >
                {scope.replace("https://www.googleapis.com/auth/", "")}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
