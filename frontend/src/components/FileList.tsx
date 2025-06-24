import React, { useState, useEffect } from "react";
import {
  File,
  Trash2,
  Download,
  Eye,
  Calendar,
  User,
  HardDrive,
  RefreshCw,
} from "lucide-react";
import { apiService } from "../services/api";
import { FileUpload } from "../types";

interface FileListProps {
  onFileSelect?: (file: FileUpload) => void;
  onFileDelete?: (file: FileUpload) => void;
  refreshTrigger?: number; // Used to trigger refresh from parent
  className?: string;
}

const FileList: React.FC<FileListProps> = ({
  onFileSelect,
  onFileDelete,
  refreshTrigger = 0,
  className = "",
}) => {
  const [files, setFiles] = useState<FileUpload[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());

  // Load files from backend
  const loadFiles = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const result = await apiService.getUserFiles();

      if (result.error) {
        setError(result.error);
      } else {
        setFiles(result.data || []);
      }
    } catch (err) {
      setError("Failed to load files");
      console.error("Error loading files:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load files on mount and when refresh is triggered
  useEffect(() => {
    loadFiles();
  }, [refreshTrigger]);

  // Handle file deletion
  const handleDelete = async (file: FileUpload) => {
    if (
      !window.confirm(`Are you sure you want to delete "${file.filename}"?`)
    ) {
      return;
    }

    try {
      setDeletingIds((prev) => new Set(prev).add(file.id));

      const result = await apiService.deleteFile(file.id);

      if (result.error) {
        throw new Error(result.error);
      }

      // Remove from local state
      setFiles((prev) => prev.filter((f) => f.id !== file.id));
      onFileDelete?.(file);
    } catch (err) {
      console.error("Error deleting file:", err);
      alert("Failed to delete file. Please try again.");
    } finally {
      setDeletingIds((prev) => {
        const newSet = new Set(prev);
        newSet.delete(file.id);
        return newSet;
      });
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  // Format date
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return (
      date.toLocaleDateString() +
      " " +
      date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    );
  };

  // Get file extension
  const getFileExtension = (filename: string): string => {
    return filename.split(".").pop()?.toUpperCase() || "";
  };

  // Get file type icon color
  const getFileTypeColor = (fileType: string): string => {
    const colors: Record<string, string> = {
      pdf: "text-red-400",
      docx: "text-blue-400",
      txt: "text-gray-400",
      md: "text-purple-400",
      xlsx: "text-green-400",
      csv: "text-green-400",
      pptx: "text-orange-400",
    };
    return colors[fileType] || "text-gray-400";
  };

  if (isLoading) {
    return (
      <div className={`${className}`}>
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-6 h-6 animate-spin text-primary-cyan" />
          <span className="ml-2 text-gray-400">Loading files...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <div className="text-center py-12">
          <div className="text-red-400 mb-4">{error}</div>
          <button
            onClick={loadFiles}
            className="px-4 py-2 bg-primary-teal/20 hover:bg-primary-teal/30 text-primary-cyan rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <div className={`${className}`}>
        <div className="text-center py-12">
          <HardDrive className="w-12 h-12 mx-auto mb-4 text-gray-500" />
          <h3 className="text-lg font-medium text-gray-300 mb-2">
            No files uploaded
          </h3>
          <p className="text-gray-500">
            Upload files to get started with AI document analysis
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* Files Grid */}
      <div className="grid grid-cols-1 gap-4">
        {files.map((file) => (
          <div
            key={file.id}
            className="group bg-bg-dark-secondary border border-primary-teal/20 rounded-lg p-4 hover:border-primary-cyan/40 transition-all duration-200"
          >
            {/* File Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                <div
                  className={`flex-shrink-0 ${getFileTypeColor(
                    file.file_type
                  )}`}
                >
                  <File className="w-8 h-8" />
                </div>

                <div className="flex-1 min-w-0">
                  <h4
                    className="text-white font-medium truncate"
                    title={file.filename}
                  >
                    {file.filename}
                  </h4>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-gray-400">
                    <span className="flex items-center">
                      <span className="font-mono bg-gray-700 px-2 py-0.5 rounded text-xs">
                        {getFileExtension(file.filename)}
                      </span>
                    </span>
                    <span>{formatFileSize(file.file_size)}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => onFileSelect?.(file)}
                  className="p-2 rounded-lg hover:bg-primary-teal/20 text-primary-cyan transition-colors"
                  title="View file"
                >
                  <Eye className="w-4 h-4" />
                </button>

                <button
                  className="p-2 rounded-lg hover:bg-primary-teal/20 text-primary-cyan transition-colors"
                  title="Download file"
                >
                  <Download className="w-4 h-4" />
                </button>

                <button
                  onClick={() => handleDelete(file)}
                  disabled={deletingIds.has(file.id)}
                  className="p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors disabled:opacity-50"
                  title="Delete file"
                >
                  {deletingIds.has(file.id) ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* File Metadata */}
            <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>Uploaded {formatDate(file.uploaded_at)}</span>
              </div>

              <div className="flex items-center space-x-1">
                <User className="w-3 h-3" />
                <span>
                  {file.is_processed ? (
                    <span className="text-primary-green">Processed</span>
                  ) : (
                    <span className="text-amber-400">Processing...</span>
                  )}
                </span>
              </div>
            </div>

            {/* Processing Error */}
            {file.processing_error && (
              <div className="mt-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-xs text-red-400">
                <strong>Processing Error:</strong> {file.processing_error}
              </div>
            )}

            {/* Google Drive Integration (if available) */}
            {file.google_drive_id && (
              <div className="mt-2 flex items-center space-x-1 text-xs text-blue-400">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span>Synced with Google Drive</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Refresh Button */}
      <div className="mt-6 text-center">
        <button
          onClick={loadFiles}
          className="px-4 py-2 text-sm bg-bg-dark-secondary hover:bg-primary-teal/10 border border-primary-teal/30 hover:border-primary-cyan/50 text-gray-300 hover:text-primary-cyan rounded-lg transition-all duration-200"
        >
          <RefreshCw className="w-4 h-4 inline mr-2" />
          Refresh Files
        </button>
      </div>
    </div>
  );
};

export default FileList;
