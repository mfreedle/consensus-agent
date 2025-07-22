import {
  Edit3,
  ExternalLink,
  FileSpreadsheet,
  FileText,
  Plus,
  Presentation,
  Search,
} from "lucide-react";
import React, { useCallback, useEffect, useState } from "react";
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

const CreateFileForm: React.FC<{
  show: boolean;
  loading: boolean;
  createType: string;
  createTitle: string;
  createContent: string;
  setCreateType: (type: string) => void;
  setCreateTitle: (title: string) => void;
  setCreateContent: (content: string) => void;
  onCreate: () => void;
  onCancel: () => void;
}> = ({
  show,
  loading,
  createType,
  createTitle,
  createContent,
  setCreateType,
  setCreateTitle,
  setCreateContent,
  onCreate,
  onCancel,
}) => {
  if (!show) return null;
  return (
    <div className="mb-4 p-4 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-800">
      <h4 className="font-semibold mb-2 text-gray-900 dark:text-white">
        Create New File
      </h4>
      <div className="space-y-3">
        <div>
          <label
            htmlFor="create-type-select"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            File Type
          </label>
          <select
            id="create-type-select"
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
          <label
            htmlFor="create-title-input"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Title
          </label>
          <input
            id="create-title-input"
            type="text"
            value={createTitle}
            onChange={(e) => setCreateTitle(e.target.value)}
            placeholder="Enter file title"
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
        {createType === "document" && (
          <div>
            <label
              htmlFor="create-content-textarea"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Initial Content (Optional)
            </label>
            <textarea
              id="create-content-textarea"
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
            onClick={onCreate}
            disabled={loading || !createTitle.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Creating..." : "Create"}
          </button>
          <button
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

const FilesList: React.FC<{
  files: GoogleDriveFile[];
  compact: boolean;
  onFileSelect?: (file: GoogleDriveFile) => void;
}> = ({ files, compact, onFileSelect }) => {
  if (files.length === 0) {
    return (
      <div
        className={`text-center text-gray-500 dark:text-gray-400 ${
          compact ? "py-4 text-xs" : "py-8"
        }`}
      >
        {compact
          ? "No files"
          : "No files found. Create your first file or connect to Google Drive."}
      </div>
    );
  }
  return (
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
  );
};

const LoadingSpinner: React.FC<{ compact: boolean }> = ({ compact }) => (
  <div
    className={`flex items-center justify-center ${compact ? "py-4" : "py-8"}`}
  >
    <div
      className={`animate-spin rounded-full border-b-2 border-blue-500 ${
        compact ? "h-4 w-4" : "h-8 w-8"
      }`}
    ></div>
  </div>
);

export const GoogleDriveFileManager: React.FC<GoogleDriveFileManagerProps> = ({
  showCreateOptions = true,
  onFileSelect,
  compact = false,
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
  const [searchQuery, setSearchQuery] = useState("");

  const loadFiles = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      let response;
      if (searchQuery.trim()) {
        response = await googleDriveService.searchFiles(token, searchQuery, {
          file_type: fileType === "all" ? undefined : fileType,
          limit: 50,
        });
      } else {
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
  }, [token, fileType, searchQuery]);

  useEffect(() => {
    if (token) {
      loadFiles();
    }
  }, [token, fileType, loadFiles, searchQuery]);

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
      setCreateTitle("");
      setCreateContent("");
      setShowCreateForm(false);
      await loadFiles();
      if (result.web_view_link) {
        window.open(result.web_view_link, "_blank");
      }
    } catch (err: any) {
      setError(`Failed to create file: ${err.message}`);
    } finally {
      setLoading(false);
    }
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

      {error && (
        <div
          className={`alert alert-error ${compact ? "text-xs p-2" : "mb-4"}`}
        >
          {error}
        </div>
      )}

      {!compact && (
        <div className="mb-4">
          <label
            htmlFor="file-type-select"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Filter by File Type
          </label>
          <select
            id="file-type-select"
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

      {!compact && (
        <div className="mb-4">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search files by name or content..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {searchQuery.trim()
              ? "Searching files..."
              : "Type to search or view recent files"}
          </p>
        </div>
      )}

      <CreateFileForm
        show={showCreateForm}
        loading={loading}
        createType={createType}
        createTitle={createTitle}
        createContent={createContent}
        setCreateType={setCreateType}
        setCreateTitle={setCreateTitle}
        setCreateContent={setCreateContent}
        onCreate={handleCreateFile}
        onCancel={() => setShowCreateForm(false)}
      />

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md">
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {loading ? (
        <LoadingSpinner compact={compact} />
      ) : (
        <FilesList
          files={files}
          compact={compact}
          onFileSelect={onFileSelect}
        />
      )}
    </div>
  );
};
