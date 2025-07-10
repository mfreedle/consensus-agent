import React, { useState, useEffect, useCallback } from "react";
import {
  FileText,
  FileSpreadsheet,
  Presentation,
  Plus,
  Edit3,
  ExternalLink,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { googleDriveService } from "../services/googleDrive";

interface GoogleDriveFile {
  id: string;
  name: string;
  type: string;
  mime_type: string;
  modified_time?: string;
  web_view_link?: string;
  owners: any[];
}

interface GoogleDriveFileManagerProps {
  showCreateOptions?: boolean;
  onFileSelect?: (file: GoogleDriveFile) => void;
  compact?: boolean; // New prop for compact sidebar view
}

export const GoogleDriveFileManager: React.FC<GoogleDriveFileManagerProps> = ({
  showCreateOptions = true,
  onFileSelect,
  compact = false, // Default to false for existing usage
}) => {
  const { token } = useAuth();
  const [files, setFiles] = useState<GoogleDriveFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileType, setFileType] = useState<string>("all");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createType, setCreateType] = useState<string>("document");
  const [createTitle, setCreateTitle] = useState("");
  const [createContent, setCreateContent] = useState("");

  const loadFiles = useCallback(async () => {
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await googleDriveService.listFiles(token, {
        file_type: fileType === "all" ? undefined : fileType,
        limit: 20,
      });
      setFiles(response.files);
    } catch (err: any) {
      setError(`Failed to load files: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [token, fileType]);

  useEffect(() => {
    if (token) {
      loadFiles();
    }
  }, [token, fileType, loadFiles]);

  const handleCreateFile = async () => {
    if (!token || !createTitle.trim()) return;

    setLoading(true);
    setError(null);

    try {
      let result;
      switch (createType) {
        case "document":
          result = await googleDriveService.createDocument(
            token,
            createTitle,
            createContent
          );
          break;
        case "spreadsheet":
          result = await googleDriveService.createSpreadsheet(
            token,
            createTitle
          );
          break;
        case "presentation":
          result = await googleDriveService.createPresentation(
            token,
            createTitle
          );
          break;
        default:
          throw new Error("Invalid file type");
      }

      // Reset form
      setCreateTitle("");
      setCreateContent("");
      setShowCreateForm(false);

      // Reload files
      await loadFiles();

      // Open the created file
      if (result.web_view_link) {
        window.open(result.web_view_link, "_blank");
      }
    } catch (err: any) {
      setError(`Failed to create file: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case "document":
        return <FileText className="h-4 w-4 text-blue-500" />;
      case "spreadsheet":
        return <FileSpreadsheet className="h-4 w-4 text-green-500" />;
      case "presentation":
        return <Presentation className="h-4 w-4 text-orange-500" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className={`google-drive-file-manager ${compact ? "compact" : ""}`}>
      {!compact && (
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Google Drive Files
          </h3>
          {showCreateOptions && (
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center space-x-2 px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Create</span>
            </button>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div
          className={`alert alert-error ${compact ? "text-xs p-2" : "mb-4"}`}
        >
          {error}
        </div>
      )}

      {/* File Type Filter - Hide in compact mode */}
      {!compact && (
        <div className="mb-4">
          <select
            value={fileType}
            onChange={(e) => setFileType(e.target.value)}
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="all">All Files</option>
            <option value="document">Documents</option>
            <option value="spreadsheet">Spreadsheets</option>
            <option value="presentation">Presentations</option>
          </select>
        </div>
      )}

      {/* Create Form */}
      {showCreateForm && (
        <div className="mb-4 p-4 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-800">
          <h4 className="font-semibold mb-2 text-gray-900 dark:text-white">
            Create New File
          </h4>

          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                File Type
              </label>
              <select
                value={createType}
                onChange={(e) => setCreateType(e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="document">Document</option>
                <option value="spreadsheet">Spreadsheet</option>
                <option value="presentation">Presentation</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Title
              </label>
              <input
                type="text"
                value={createTitle}
                onChange={(e) => setCreateTitle(e.target.value)}
                placeholder="Enter file title"
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>

            {createType === "document" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Initial Content (Optional)
                </label>
                <textarea
                  value={createContent}
                  onChange={(e) => setCreateContent(e.target.value)}
                  placeholder="Enter initial content..."
                  rows={4}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>
            )}

            <div className="flex space-x-2">
              <button
                onClick={handleCreateFile}
                disabled={loading || !createTitle.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Creating..." : "Create"}
              </button>
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md">
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {/* Files List */}
      {loading ? (
        <div
          className={`flex items-center justify-center ${
            compact ? "py-4" : "py-8"
          }`}
        >
          <div
            className={`animate-spin rounded-full border-b-2 border-blue-500 ${
              compact ? "h-4 w-4" : "h-8 w-8"
            }`}
          ></div>
        </div>
      ) : files.length === 0 ? (
        <div
          className={`text-center text-gray-500 dark:text-gray-400 ${
            compact ? "py-4 text-xs" : "py-8"
          }`}
        >
          {compact
            ? "No files"
            : "No files found. Create your first file or connect to Google Drive."}
        </div>
      ) : (
        <div className={compact ? "space-y-1" : "space-y-2"}>
          {files.map((file) => (
            <div
              key={file.id}
              className={`flex items-center justify-between border border-gray-200 dark:border-gray-700 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${
                compact ? "p-2" : "p-3"
              }`}
            >
              <div className="flex items-center space-x-2 min-w-0 flex-1">
                {getFileIcon(file.type)}
                <div className="min-w-0 flex-1">
                  <h4
                    className={`font-medium text-gray-900 dark:text-white truncate ${
                      compact ? "text-xs" : "text-sm"
                    }`}
                  >
                    {file.name}
                  </h4>
                  {!compact && (
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Modified: {formatDate(file.modified_time)}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-1 flex-shrink-0">
                {onFileSelect && (
                  <button
                    onClick={() => onFileSelect(file)}
                    className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                    title="Select file"
                  >
                    <Edit3 className={compact ? "h-3 w-3" : "h-4 w-4"} />
                  </button>
                )}
                {file.web_view_link && (
                  <button
                    onClick={() => window.open(file.web_view_link, "_blank")}
                    className="p-1 text-gray-400 hover:text-green-500 transition-colors"
                    title="Open in Google Drive"
                  >
                    <ExternalLink className={compact ? "h-3 w-3" : "h-4 w-4"} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
