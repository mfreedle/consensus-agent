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
  Search,
  ChevronLeft,
  ChevronRight,
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
  showPagination?: boolean;
  filesPerPage?: number;
}

const FileList: React.FC<FileListProps> = ({
  onFileSelect,
  onFileDelete,
  refreshTrigger = 0,
  className = "",
  showPagination = true,
  filesPerPage = 10,
}) => {
  const [files, setFiles] = useState<FileUpload[]>([]);
  const [filteredFiles, setFilteredFiles] = useState<FileUpload[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<FileUpload | null>(null);
  const { addError, clearErrors } = useErrorHandler();

  // Load files from backend
  const loadFiles = useCallback(async () => {
    try {
      setIsLoading(true);
      clearErrors();

      const result = await enhancedApiService.getUserFiles();
      // Backend returns {files: []} so we need to extract the files array
      const filesData = result?.files || result || [];
      const filesList = Array.isArray(filesData) ? filesData : [];
      setFiles(filesList);
      setFilteredFiles(filesList);
      setCurrentPage(1);
    } catch (error) {
      addError(error, "api", "Failed to load files");
    } finally {
      setIsLoading(false);
    }
  }, [addError, clearErrors]);

  // Filter files based on search term
  useEffect(() => {
    const filtered = files.filter(
      (file) =>
        file.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        file.file_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        file.id.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredFiles(filtered);
    setCurrentPage(1);
  }, [files, searchTerm]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredFiles.length / filesPerPage);
  const startIndex = (currentPage - 1) * filesPerPage;
  const endIndex = startIndex + filesPerPage;
  const currentFiles = showPagination
    ? filteredFiles.slice(startIndex, endIndex)
    : filteredFiles;

  // Load files on mount and when refresh is triggered
  useEffect(() => {
    loadFiles();
  }, [loadFiles, refreshTrigger]);

  // Handle file deletion with enhanced confirmation
  const handleDeleteRequest = (file: FileUpload) => {
    setFileToDelete(file);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!fileToDelete) return;

    const file = fileToDelete;
    console.log("Delete confirmed for file:", file.filename, "ID:", file.id);

    try {
      console.log("Starting delete process for file ID:", file.id);
      setDeletingIds((prev) => new Set(prev).add(file.id));

      console.log("Calling API to delete file...");
      const result = await enhancedApiService.deleteFile(file.id);
      console.log("API delete result:", result);

      // Remove from local state
      setFiles((prev) => {
        const newFiles = prev.filter((f) => f.id !== file.id);
        console.log(
          "Updated files list, removed file. New count:",
          newFiles.length
        );
        return newFiles;
      });

      onFileDelete?.(file);
      console.log("File deletion completed successfully");
    } catch (error) {
      console.error("Error during file deletion:", error);
      addError(error, "api", `Failed to delete file "${file.filename}"`);
    } finally {
      setDeletingIds((prev) => {
        const newSet = new Set(prev);
        newSet.delete(file.id);
        return newSet;
      });
      setShowDeleteModal(false);
      setFileToDelete(null);
    }
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setFileToDelete(null);
  };

  // Handle file download
  const handleDownload = (file: FileUpload) => {
    try {
      // Create download URL - assuming backend serves files at /api/files/{id}/download
      const downloadUrl = `/api/files/${file.id}/download`;

      // Create a temporary anchor element and trigger download
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = file.filename;
      link.style.display = "none";

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Download failed:", error);
      addError("Failed to download file", "api");
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
      {/* Search and Filter */}
      {files.length > 0 && (
        <div className="mb-4 space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search files by name, type, or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-gray-200 placeholder-gray-400 focus:border-primary-cyan focus:outline-none"
            />
          </div>

          {searchTerm && (
            <div className="text-xs text-gray-400">
              Found {filteredFiles.length} of {files.length} files
            </div>
          )}
        </div>
      )}

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
        {currentFiles.map((file) => (
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
                  <button
                    onClick={() => handleDownload(file)}
                    className="p-2 rounded-lg hover:bg-primary-teal/20 text-primary-cyan transition-colors"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </Tooltip>

                <Tooltip content="Delete file permanently">
                  <button
                    onClick={() => handleDeleteRequest(file)}
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

      {/* Pagination */}
      {showPagination && totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center space-x-2">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="p-2 rounded-lg hover:bg-gray-700/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4 text-gray-400" />
          </button>

          <div className="flex items-center space-x-1">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  currentPage === page
                    ? "bg-primary-cyan text-gray-900"
                    : "hover:bg-gray-700/50 text-gray-400"
                }`}
              >
                {page}
              </button>
            ))}
          </div>

          <button
            onClick={() =>
              setCurrentPage((prev) => Math.min(totalPages, prev + 1))
            }
            disabled={currentPage === totalPages}
            className="p-2 rounded-lg hover:bg-gray-700/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      )}

      {/* Enhanced Delete Confirmation Modal */}
      {showDeleteModal && fileToDelete && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg border border-gray-600 p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-white mb-4">
              Confirm File Deletion
            </h3>

            <div className="space-y-3 mb-6">
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
                <div className="flex items-center space-x-3">
                  <div
                    className={`flex-shrink-0 ${getFileTypeColor(
                      fileToDelete.file_type
                    )}`}
                  >
                    <File className="w-6 h-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium truncate">
                      {fileToDelete.filename}
                    </p>
                    <p className="text-xs text-gray-400 font-mono">
                      ID: {fileToDelete.id}
                    </p>
                  </div>
                </div>

                <div className="mt-2 text-xs text-gray-500 space-y-1">
                  <div>Size: {formatFileSize(fileToDelete.file_size)}</div>
                  <div>Uploaded: {formatDate(fileToDelete.uploaded_at)}</div>
                  <div>Type: {fileToDelete.file_type}</div>
                </div>
              </div>

              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                <p className="text-red-400 text-sm">
                  ⚠️ This action cannot be undone. The file will be permanently
                  removed from your knowledge base.
                </p>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                disabled={deletingIds.has(fileToDelete.id)}
                className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                {deletingIds.has(fileToDelete.id) ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Deleting...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" />
                    <span>Delete File</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

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
