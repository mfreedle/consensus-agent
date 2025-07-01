import React, { useState, useEffect, useCallback } from "react";
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
import { enhancedApiService } from "../services/enhancedApi";
import { useErrorHandler } from "../hooks/useErrorHandler";
import LoadingSkeleton from "./LoadingSkeleton";
import Tooltip from "./Tooltip";
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
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());
  const { addError, clearErrors } = useErrorHandler();

  // Load files from backend
  const loadFiles = useCallback(async () => {
    try {
      setIsLoading(true);
      clearErrors();

      const result = await enhancedApiService.getUserFiles();
      // Backend returns {files: []} so we need to extract the files array
      const filesData = result?.files || result || [];
      setFiles(Array.isArray(filesData) ? filesData : []);
    } catch (error) {
      addError(error, "api", "Failed to load files");
    } finally {
      setIsLoading(false);
    }
  }, [addError, clearErrors]);

  // Load files on mount and when refresh is triggered
  useEffect(() => {
    loadFiles();
  }, [loadFiles, refreshTrigger]);

  // Handle file deletion
  const handleDelete = useCallback(
    async (file: FileUpload) => {
      if (
        !window.confirm(`Are you sure you want to delete "${file.filename}"?`)
      ) {
        return;
      }

      try {
        setDeletingIds((prev) => new Set(prev).add(file.id));

        await enhancedApiService.deleteFile(file.id);

        // Remove from local state
        setFiles((prev) => prev.filter((f) => f.id !== file.id));
        onFileDelete?.(file);
      } catch (error) {
        addError(error, "api", `Failed to delete file "${file.filename}"`);
      } finally {
        setDeletingIds((prev) => {
          const newSet = new Set(prev);
          newSet.delete(file.id);
          return newSet;
        });
      }
    },
    [addError, onFileDelete]
  );

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
        <div className="space-y-4">
          {/* File list skeleton */}
          {[...Array(3)].map((_, i) => (
            <LoadingSkeleton key={i} variant="card" className="h-16" />
          ))}
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
      {/* Knowledge Base Summary */}
      {files.length > 0 && (
        <div className="mb-4 p-3 bg-gray-800/30 rounded-lg border border-gray-700/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-primary-cyan" />
              <span className="text-sm font-medium text-gray-300">
                Knowledge Base Files
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {files.length} {files.length === 1 ? "file" : "files"}
            </div>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Total storage:{" "}
            {formatFileSize(
              files.reduce((total, file) => total + (file.file_size || 0), 0)
            )}
          </div>
        </div>
      )}

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
                <Tooltip content="View file details and content">
                  <button
                    onClick={() => onFileSelect?.(file)}
                    className="p-2 rounded-lg hover:bg-primary-teal/20 text-primary-cyan transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </Tooltip>

                <Tooltip content="Download file to your device">
                  <button className="p-2 rounded-lg hover:bg-primary-teal/20 text-primary-cyan transition-colors">
                    <Download className="w-4 h-4" />
                  </button>
                </Tooltip>

                <Tooltip content="Delete file permanently">
                  <button
                    onClick={() => handleDelete(file)}
                    disabled={deletingIds.has(file.id)}
                    className="p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors disabled:opacity-50"
                  >
                    {deletingIds.has(file.id) ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </Tooltip>
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
