import React, { useState } from "react";
import { X, Paperclip, Database } from "lucide-react";
import ModernFileUpload from "./ModernFileUpload";

interface FileUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: "attach" | "knowledge";
  onFilesUploaded?: (files: any[]) => void;
  onFileAttached?: (file: File, uploadedFileId?: string) => void;
}

const FileUploadModal: React.FC<FileUploadModalProps> = ({
  isOpen,
  onClose,
  mode,
  onFilesUploaded,
  onFileAttached,
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);

  const handleFilesUploaded = (files: any[]) => {
    setUploadedFiles((prev) => [...prev, ...files]);
    onFilesUploaded?.(files);
  };

  const handleFileAttached = (file: File, uploadedFileId?: string) => {
    console.log(
      "FileUploadModal: handleFileAttached called with file:",
      file.name,
      "ID:",
      uploadedFileId
    );
    onFileAttached?.(file, uploadedFileId);
    // For attach mode, close modal immediately after attaching
    if (mode === "attach") {
      console.log("FileUploadModal: Closing modal after file attachment");
      onClose();
    }
  };

  const handleClose = () => {
    setUploadedFiles([]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="file-upload-modal-overlay" onClick={handleClose}>
      <div className="file-upload-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-section">
            <div className="modal-icon">
              {mode === "attach" ? (
                <Paperclip className="w-6 h-6 text-primary-cyan" />
              ) : (
                <Database className="w-6 h-6 text-primary-teal" />
              )}
            </div>
            <div>
              <h2 className="modal-title">
                {mode === "attach"
                  ? "Attach Files"
                  : "Upload to Knowledge Base"}
              </h2>
              <p className="modal-subtitle">
                {mode === "attach"
                  ? "Attach files to this conversation for immediate reference"
                  : "Add documents to your persistent knowledge base"}
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="modal-close-btn"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="modal-content">
          <ModernFileUpload
            mode={mode}
            onFilesUploaded={handleFilesUploaded}
            onFileAttached={handleFileAttached}
            maxFiles={mode === "attach" ? 5 : 10}
          />

          {/* Upload Summary */}
          {uploadedFiles.length > 0 && mode === "knowledge" && (
            <div className="upload-summary">
              <h3 className="summary-title">Successfully Uploaded</h3>
              <div className="summary-list">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="summary-item">
                    <span className="summary-filename">{file.filename}</span>
                    <span className="summary-size">
                      {file.size ? `${Math.round(file.size / 1024)}KB` : ""}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <div className="footer-info">
            {mode === "attach" ? (
              <p className="footer-text">
                Attached files will be available for this conversation only
              </p>
            ) : (
              <p className="footer-text">
                Uploaded files will be processed and available across all
                conversations
              </p>
            )}
          </div>
          <div className="footer-actions">
            <button onClick={handleClose} className="btn btn-secondary">
              {uploadedFiles.length > 0 ? "Done" : "Cancel"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUploadModal;
