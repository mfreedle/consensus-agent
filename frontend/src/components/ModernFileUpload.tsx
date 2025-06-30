import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  X,
  File,
  FileText,
  Image,
  FileSpreadsheet,
  Presentation,
  AlertCircle,
  CheckCircle,
  Loader2,
  Paperclip,
  Database,
} from "lucide-react";
import { enhancedApiService } from "../services/enhancedApi";
import { SUPPORTED_FILE_TYPES } from "../types";
import { useErrorHandler } from "../hooks/useErrorHandler";

interface UploadFile {
  file: File;
  id: string;
  progress: number;
  status: "uploading" | "success" | "error";
  error?: string;
  uploadedFileId?: string;
}

interface ModernFileUploadProps {
  mode: "attach" | "knowledge"; // attach = temporary, knowledge = permanent
  onFilesUploaded?: (files: any[]) => void;
  onFileAttached?: (file: File) => void;
  maxFiles?: number;
  className?: string;
  children?: React.ReactNode;
}

const ModernFileUpload: React.FC<ModernFileUploadProps> = ({
  mode,
  onFilesUploaded,
  onFileAttached,
  maxFiles = mode === "attach" ? 5 : 10,
  className = "",
  children,
}) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadFile[]>([]);
  const { addError } = useErrorHandler();

  const getFileIcon = (file: File) => {
    const extension = "." + file.name.split(".").pop()?.toLowerCase();
    const fileType = SUPPORTED_FILE_TYPES.find(
      (type) => type.extension === extension
    );

    switch (fileType?.category) {
      case "document":
        return <FileText className="w-5 h-5 text-blue-400" />;
      case "spreadsheet":
        return <FileSpreadsheet className="w-5 h-5 text-green-400" />;
      case "presentation":
        return <Presentation className="w-5 h-5 text-orange-400" />;
      case "image":
        return <Image className="w-5 h-5 text-purple-400" />;
      default:
        return <File className="w-5 h-5 text-gray-400" />;
    }
  };

  const validateFile = (file: File): { isValid: boolean; error?: string } => {
    const extension = "." + file.name.split(".").pop()?.toLowerCase();
    const fileType = SUPPORTED_FILE_TYPES.find(
      (type) => type.extension === extension
    );

    if (!fileType) {
      return {
        isValid: false,
        error: `Unsupported file type. Supported: ${SUPPORTED_FILE_TYPES.map(
          (t) => t.extension
        ).join(", ")}`,
      };
    }

    const maxSizeBytes = fileType.maxSize * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return {
        isValid: false,
        error: `File too large. Maximum size: ${fileType.maxSize}MB`,
      };
    }

    return { isValid: true };
  };

  const uploadFile = useCallback(
    async (file: File, uploadFileObj: UploadFile) => {
      try {
        if (mode === "attach") {
          // For attach mode, just notify parent component
          onFileAttached?.(file);
          setUploadingFiles((prev) =>
            prev.map((f) =>
              f.id === uploadFileObj.id
                ? { ...f, status: "success", progress: 100 }
                : f
            )
          );
        } else {
          // For knowledge mode, upload to server
          const response = await enhancedApiService.uploadFile(
            file,
            (progress) => {
              setUploadingFiles((prev) =>
                prev.map((f) =>
                  f.id === uploadFileObj.id ? { ...f, progress } : f
                )
              );
            }
          );

          setUploadingFiles((prev) =>
            prev.map((f) =>
              f.id === uploadFileObj.id
                ? {
                    ...f,
                    status: "success",
                    progress: 100,
                    uploadedFileId: response.file_id,
                  }
                : f
            )
          );

          onFilesUploaded?.([response]);
        }
      } catch (error) {
        console.error("Upload error:", error);
        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFileObj.id
              ? {
                  ...f,
                  status: "error",
                  error:
                    error instanceof Error ? error.message : "Upload failed",
                }
              : f
          )
        );
        addError(error, "upload", "File upload failed");
      }
    },
    [mode, onFileAttached, onFilesUploaded, addError]
  );

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      // Validate files
      const validFiles: File[] = [];
      for (const file of acceptedFiles) {
        const validation = validateFile(file);
        if (validation.isValid) {
          validFiles.push(file);
        } else {
          addError(
            new Error(validation.error),
            "upload",
            `${file.name}: ${validation.error}`
          );
        }
      }

      if (validFiles.length === 0) return;

      // Check max files limit
      if (uploadingFiles.length + validFiles.length > maxFiles) {
        addError(
          new Error(`Too many files`),
          "upload",
          `Maximum ${maxFiles} files allowed. Currently have ${uploadingFiles.length}.`
        );
        return;
      }

      // Create upload file objects
      const newUploadFiles: UploadFile[] = validFiles.map((file) => ({
        file,
        id: Date.now() + Math.random().toString(),
        progress: 0,
        status: "uploading" as const,
      }));

      setUploadingFiles((prev) => [...prev, ...newUploadFiles]);

      // Upload files
      for (const uploadFileObj of newUploadFiles) {
        uploadFile(uploadFileObj.file, uploadFileObj);
      }
    },
    [uploadingFiles.length, maxFiles, addError, uploadFile]
  );

  const removeFile = (fileId: string) => {
    setUploadingFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      multiple: true,
      maxFiles,
      accept: {
        "application/pdf": [".pdf"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
          [".docx"],
        "text/plain": [".txt"],
        "text/markdown": [".md"],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
          ".xlsx",
        ],
        "text/csv": [".csv"],
        "application/vnd.openxmlformats-officedocument.presentationml.presentation":
          [".pptx"],
      },
    });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className={`modern-file-upload ${className}`}>
      <div
        {...getRootProps()}
        className={`upload-dropzone ${isDragActive ? "drag-active" : ""} ${
          isDragReject ? "drag-reject" : ""
        }`}
      >
        <input {...getInputProps()} />

        {children || (
          <div className="upload-content">
            <div className="upload-icon">
              {mode === "attach" ? (
                <Paperclip className="w-8 h-8 text-primary-cyan" />
              ) : (
                <Database className="w-8 h-8 text-primary-teal" />
              )}
            </div>

            <div className="upload-text">
              <h3 className="upload-title">
                {mode === "attach"
                  ? "Attach Files"
                  : "Upload to Knowledge Base"}
              </h3>
              <p className="upload-subtitle">
                {isDragActive
                  ? "Drop files here..."
                  : mode === "attach"
                  ? "Drag & drop files or click to attach them to this conversation"
                  : "Drag & drop files or click to add them to your knowledge base"}
              </p>
              <p className="upload-info">
                Supports: PDF, DOCX, TXT, MD, XLSX, CSV, PPTX (max {maxFiles}{" "}
                files)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Upload Progress */}
      {uploadingFiles.length > 0 && (
        <div className="upload-progress-list">
          {uploadingFiles.map((uploadFile) => (
            <div key={uploadFile.id} className="upload-progress-item">
              <div className="upload-file-info">
                <div className="file-icon">{getFileIcon(uploadFile.file)}</div>
                <div className="file-details">
                  <div className="file-name">{uploadFile.file.name}</div>
                  <div className="file-size">
                    {formatFileSize(uploadFile.file.size)}
                  </div>
                </div>
              </div>

              <div className="upload-status">
                {uploadFile.status === "uploading" && (
                  <>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${uploadFile.progress}%` }}
                      />
                    </div>
                    <Loader2 className="w-4 h-4 animate-spin text-primary-cyan" />
                  </>
                )}

                {uploadFile.status === "success" && (
                  <CheckCircle className="w-4 h-4 text-green-400" />
                )}

                {uploadFile.status === "error" && (
                  <AlertCircle className="w-4 h-4 text-red-400" />
                )}

                <button
                  onClick={() => removeFile(uploadFile.id)}
                  className="remove-file-btn"
                  aria-label="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {uploadFile.status === "error" && uploadFile.error && (
                <div className="upload-error">{uploadFile.error}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModernFileUpload;
