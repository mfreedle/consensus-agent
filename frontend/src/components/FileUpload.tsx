import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, File, AlertCircle, CheckCircle } from "lucide-react";
import { apiService } from "../services/api";
import { SUPPORTED_FILE_TYPES } from "../types";
import { useError } from "../contexts/ErrorContext";
import { useLoadingState } from "./LoadingIndicator";

interface FileUploadProps {
  onUploadSuccess?: (file: any) => void;
  onUploadError?: (error: string) => void;
  maxFiles?: number;
  className?: string;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: "uploading" | "success" | "error";
  error?: string;
  id: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadError,
  maxFiles = 10,
  className = "",
}) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const { addError } = useError();
  const loadingState = useLoadingState();

  // Validate file type and size
  const validateFile = (file: File): { isValid: boolean; error?: string } => {
    const fileExtension = "." + file.name.split(".").pop()?.toLowerCase();
    const supportedType = SUPPORTED_FILE_TYPES.find(
      (type) => type.extension === fileExtension
    );

    if (!supportedType) {
      return {
        isValid: false,
        error: `Unsupported file type. Supported types: ${SUPPORTED_FILE_TYPES.map(
          (t) => t.extension
        ).join(", ")}`,
      };
    }

    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > supportedType.maxSize) {
      return {
        isValid: false,
        error: `File too large. Maximum size for ${fileExtension} files is ${supportedType.maxSize}MB`,
      };
    }

    return { isValid: true };
  };

  // Handle file upload with enhanced error handling
  const uploadFile = useCallback(
    async (file: File): Promise<void> => {
      const fileId = Date.now().toString() + Math.random().toString(36);

      // Add to uploading files list
      const uploadingFile: UploadingFile = {
        file,
        progress: 0,
        status: "uploading",
        id: fileId,
      };

      setUploadingFiles((prev) => [...prev, uploadingFile]);

      try {
        // Show global loading for first file
        if (uploadingFiles.length === 0) {
          loadingState.setLoading(
            true,
            "Uploading file...",
            `Processing ${file.name}`
          );
        }

        // Simulate progress updates (in real implementation, you'd use XMLHttpRequest for progress)
        const updateProgress = (progress: number) => {
          setUploadingFiles((prev) =>
            prev.map((f) => (f.id === fileId ? { ...f, progress } : f))
          );

          if (uploadingFiles.length === 0) {
            loadingState.updateProgress(progress);
          }
        };

        updateProgress(20);
        await new Promise((resolve) => setTimeout(resolve, 500));
        updateProgress(50);

        const result = await apiService.uploadFile(file);

        if (result.error) {
          throw new Error(result.error);
        }

        updateProgress(100);

        // Mark as success
        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.id === fileId ? { ...f, status: "success", progress: 100 } : f
          )
        );

        onUploadSuccess?.(result.data);

        // Remove from list after 3 seconds
        setTimeout(() => {
          setUploadingFiles((prev) => prev.filter((f) => f.id !== fileId));
        }, 3000);
      } catch (error) {
        console.error("File upload error:", error);

        const errorMessage =
          error instanceof Error ? error.message : "Upload failed";

        // Mark file as failed
        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.id === fileId ? { ...f, status: "error", error: errorMessage } : f
          )
        );

        // Add to global error system
        addError(error, "upload", `Failed to upload ${file.name}`);
        onUploadError?.(errorMessage);
      } finally {
        // Clear global loading if this was the only file
        if (uploadingFiles.length === 0) {
          loadingState.setLoading(false);
        }
      }
    },
    [
      uploadingFiles.length,
      loadingState,
      onUploadSuccess,
      addError,
      onUploadError,
    ]
  );
  // Handle dropped files
  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      setIsUploading(true);

      for (const file of acceptedFiles) {
        const validation = validateFile(file);

        if (!validation.isValid) {
          addError(validation.error || "Invalid file", "validation");
          onUploadError?.(validation.error || "Invalid file");
          continue;
        }

        await uploadFile(file);
      }

      setIsUploading(false);
    },
    [addError, onUploadError, uploadFile]
  );

  // Remove file from uploading list
  const removeFile = (fileId: string) => {
    setUploadingFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      maxFiles,
      disabled: isUploading,
      accept: SUPPORTED_FILE_TYPES.reduce((acc, type) => {
        acc[type.mimeType] = [type.extension];
        return acc;
      }, {} as Record<string, string[]>),
    });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };
  const getFileIcon = (filename: string) => {
    // Return appropriate icon based on file type
    return <File className="w-4 h-4" />;
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-4 md:p-8 text-center cursor-pointer transition-all duration-200
          ${
            isDragActive && !isDragReject
              ? "border-primary-cyan bg-primary-cyan/5"
              : isDragReject
              ? "border-red-500 bg-red-500/5"
              : "border-primary-teal/30 hover:border-primary-cyan/50 bg-bg-dark-secondary/50"
          }
          ${isUploading ? "opacity-50 cursor-not-allowed" : ""}
        `}
      >
        <input {...getInputProps()} />

        <Upload
          className={`w-8 h-8 md:w-12 md:h-12 mx-auto mb-3 md:mb-4 ${
            isDragActive ? "text-primary-cyan" : "text-gray-400"
          }`}
        />

        {isDragActive ? (
          <div>
            <p className="text-base md:text-lg font-medium text-primary-cyan mb-1 md:mb-2">
              {isDragReject
                ? "Some files are not supported"
                : "Drop files here"}
            </p>
            <p className="text-xs md:text-sm text-gray-400">
              {isDragReject
                ? "Please check file types and sizes"
                : "Release to upload"}
            </p>
          </div>
        ) : (
          <div>
            <p className="text-base md:text-lg font-medium text-white mb-1 md:mb-2">
              Drag & drop files here, or click to select
            </p>
            <p className="text-xs md:text-sm text-gray-400 mb-2 md:mb-4">
              Support for PDF, DOCX, TXT, MD, XLSX, CSV, PPTX
            </p>
            <p className="text-xs text-gray-500">
              Maximum {maxFiles} files, up to 50MB each
            </p>
          </div>
        )}
      </div>

      {/* Uploading Files List */}
      {uploadingFiles.length > 0 && (
        <div className="mt-4 md:mt-6 space-y-2 md:space-y-3">
          <h4 className="text-sm font-medium text-gray-300">Uploading Files</h4>

          {uploadingFiles.map((uploadingFile) => (
            <div
              key={uploadingFile.id}
              className="flex items-center space-x-2 md:space-x-3 p-2 md:p-3 bg-bg-dark-secondary rounded-lg border border-primary-teal/20"
            >
              {/* File Icon */}
              <div className="flex-shrink-0">
                {uploadingFile.status === "success" ? (
                  <CheckCircle className="w-4 h-4 md:w-5 md:h-5 text-primary-green" />
                ) : uploadingFile.status === "error" ? (
                  <AlertCircle className="w-4 h-4 md:w-5 md:h-5 text-red-500" />
                ) : (
                  getFileIcon(uploadingFile.file.name)
                )}
              </div>

              {/* File Info */}
              <div className="flex-1 min-w-0">
                <p className="text-xs md:text-sm font-medium text-white truncate">
                  {uploadingFile.file.name}
                </p>
                <p className="text-xs text-gray-400">
                  {formatFileSize(uploadingFile.file.size)}
                </p>

                {/* Error Message */}
                {uploadingFile.status === "error" && uploadingFile.error && (
                  <p className="text-xs text-red-400 mt-1">
                    {uploadingFile.error}
                  </p>
                )}
              </div>

              {/* Progress Bar */}
              {uploadingFile.status === "uploading" && (
                <div className="flex-1 max-w-24 md:max-w-32">
                  <div className="w-full bg-gray-700 rounded-full h-1.5 md:h-2">
                    <div
                      className="bg-primary-cyan h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadingFile.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1 text-center">
                    {uploadingFile.progress}%
                  </p>
                </div>
              )}

              {/* Status Text */}
              {uploadingFile.status !== "uploading" && (
                <div className="text-xs">
                  {uploadingFile.status === "success" ? (
                    <span className="text-primary-green">Complete</span>
                  ) : (
                    <span className="text-red-400">Failed</span>
                  )}
                </div>
              )}

              {/* Remove Button */}
              <button
                onClick={() => removeFile(uploadingFile.id)}
                className="flex-shrink-0 p-1 rounded hover:bg-gray-700 transition-colors"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Supported File Types */}
      <div className="mt-4 text-xs text-gray-500">
        <details className="cursor-pointer">
          <summary className="hover:text-gray-400">
            Supported file types
          </summary>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {SUPPORTED_FILE_TYPES.map((type) => (
              <div key={type.extension} className="flex justify-between">
                <span>{type.extension.toUpperCase()}</span>
                <span>up to {type.maxSize}MB</span>
              </div>
            ))}
          </div>
        </details>
      </div>
    </div>
  );
};

export default FileUpload;
