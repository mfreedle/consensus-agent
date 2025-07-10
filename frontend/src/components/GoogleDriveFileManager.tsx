import React, { useState, useEffect, useCallback } from "react";
import {
  FileText,
  FileSpreadsheet,
  Presentation,
  Plus,
  Edit3,
  ExternalLink,
  Search,
  Folder,
  MapPin,
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
  path?: string; // Optional path for files with full paths
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

  // New search and navigation state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchMode, setSearchMode] = useState(false);
  const [viewMode, setViewMode] = useState<"recent" | "search" | "paths">(
    "recent"
  );
  const [currentFolder, setCurrentFolder] = useState<string | null>(null);
  const [folderPath, setFolderPath] = useState<string[]>([]);

  const loadFiles = useCallback(async () => {
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      let response;

      if (viewMode === "search" && searchQuery.trim()) {
        // Search for files
        response = await googleDriveService.searchFiles(token, searchQuery, {
          file_type: fileType === "all" ? undefined : fileType,
          limit: 50,
        });
      } else if (viewMode === "paths") {
        // List all files with their full paths
        response = await googleDriveService.listFilesWithPaths(token, {
          file_type: fileType === "all" ? undefined : fileType,
          limit: 100,
        });
      } else if (currentFolder) {
        // List folder contents
        response = await googleDriveService.listFolderContents(
          token,
          currentFolder,
          {
            file_type: fileType === "all" ? undefined : fileType,
            limit: 50,
          }
        );
      } else {
        // Default: recent files
        response = await googleDriveService.listFiles(token, {
          file_type: fileType === "all" ? undefined : fileType,
          limit: 20,
        });
      }

      setFiles(response.files);
    } catch (err: any) {
      setError(`Failed to load files: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [token, fileType, viewMode, searchQuery, currentFolder]);

  useEffect(() => {
    if (token) {
      loadFiles();
    }
  }, [token, fileType, loadFiles, viewMode, searchQuery]);

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

      {/* View Mode Selector - New feature */}
      {!compact && (
        <div className="mb-4">
          <div className="flex space-x-2">
            <button
              onClick={() => {
                setViewMode("recent");
                setSearchQuery("");
              }}
              className={`px-3 py-1 rounded-md text-xs font-medium ${
                viewMode === "recent"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
              }`}
            >
              Recent
            </button>
            <button
              onClick={() => setViewMode("search")}
              className={`px-3 py-1 rounded-md text-xs font-medium ${
                viewMode === "search"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
              }`}
            >
              <Search className="h-3 w-3 inline mr-1" />
              Search
            </button>
            <button
              onClick={() => {
                setViewMode("paths");
                setSearchQuery("");
              }}
              className={`px-3 py-1 rounded-md text-xs font-medium ${
                viewMode === "paths"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
              }`}
            >
              <Folder className="h-3 w-3 inline mr-1" />
              Paths
            </button>
          </div>
        </div>
      )}

      {/* Search Bar - Show when in search mode */}
      {viewMode === "search" && !compact && (
        <div className="mb-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search files by name or content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  loadFiles();
                }
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <button
              onClick={loadFiles}
              className="absolute right-2 top-1 px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
            >
              Search
            </button>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Search includes file names, content, and files in all subfolders
          </p>
        </div>
      )}

      {/* Search Bar - New feature */}
      <div className="mb-4">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search files..."
            className="w-full p-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          <button
            onClick={() => setViewMode("search")}
            className="absolute inset-y-0 right-0 flex items-center pr-3"
          >
            <Search className="h-5 w-5 text-gray-400" />
          </button>
        </div>
      </div>

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
                    <div className="space-y-1">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Modified: {formatDate(file.modified_time)}
                      </p>
                      {file.path && viewMode === "paths" && (
                        <p className="text-xs text-blue-600 dark:text-blue-400 flex items-center">
                          <MapPin className="h-3 w-3 mr-1" />
                          {file.path}
                        </p>
                      )}
                    </div>
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
