import React, { useState, useEffect, useCallback } from "react";
import {
  History,
  ArrowLeft,
  Clock,
  FileText,
  RotateCcw,
  Eye,
} from "lucide-react";
import LoadingIndicator from "./LoadingIndicator";
import {
  approvalService,
  VersionHistory,
  DocumentVersion,
} from "../services/approvalService";

interface FileVersionHistoryProps {
  fileId: number;
  fileName: string;
  onBack: () => void;
}

export const FileVersionHistory: React.FC<FileVersionHistoryProps> = ({
  fileId,
  fileName,
  onBack,
}) => {
  const [versionHistory, setVersionHistory] = useState<VersionHistory | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rollbackLoading, setRollbackLoading] = useState<number | null>(null);
  const [selectedVersion, setSelectedVersion] =
    useState<DocumentVersion | null>(null);

  const loadVersionHistory = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const history = await approvalService.getFileVersionHistory(fileId);
      setVersionHistory(history);
    } catch (error) {
      console.error("Failed to load version history:", error);
      setError("Failed to load version history");
    } finally {
      setLoading(false);
    }
  }, [fileId]);

  useEffect(() => {
    loadVersionHistory();
  }, [loadVersionHistory]);

  const handleRollback = async (versionNumber: number) => {
    if (
      !window.confirm(
        `Are you sure you want to rollback to version ${versionNumber}? This will create a new version with the content from version ${versionNumber}.`
      )
    ) {
      return;
    }

    try {
      setRollbackLoading(versionNumber);
      await approvalService.rollbackFileVersion(fileId, versionNumber);
      // Reload version history after rollback
      await loadVersionHistory();
    } catch (error) {
      console.error("Failed to rollback:", error);
      setError(`Failed to rollback to version ${versionNumber}`);
    } finally {
      setRollbackLoading(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatFileSize = (bytes: number | undefined) => {
    if (!bytes) return "Unknown size";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-center py-8">
          <LoadingIndicator isLoading={true} size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>

        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-gray-600" />
          <h1 className="text-xl font-semibold text-gray-900">{fileName}</h1>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {versionHistory && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          <div className="flex items-center space-x-2 mb-4">
            <History className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Version History
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="text-sm text-blue-600 font-medium">
                Current Version
              </div>
              <div className="text-lg font-semibold text-blue-900">
                {versionHistory.current_version}
              </div>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="text-sm text-green-600 font-medium">
                Total Versions
              </div>
              <div className="text-lg font-semibold text-green-900">
                {versionHistory.total_versions}
              </div>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <div className="text-sm text-purple-600 font-medium">
                File Name
              </div>
              <div className="text-lg font-semibold text-purple-900 truncate">
                {versionHistory.file_name}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Version List */}
      <div className="space-y-4">
        {versionHistory?.versions.map((version) => (
          <div
            key={version.id}
            className={`bg-white border rounded-lg p-4 ${
              version.version_number === versionHistory.current_version
                ? "border-blue-300 bg-blue-50"
                : "border-gray-200"
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${
                      version.version_number === versionHistory.current_version
                        ? "bg-blue-100 text-blue-800"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    Version {version.version_number}
                  </span>
                  {version.version_number ===
                    versionHistory.current_version && (
                    <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                      Current
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatDate(version.created_at)}</span>
                  </span>
                  <span>{formatFileSize(version.file_size)}</span>
                  <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                    {version.version_hash.substring(0, 8)}
                  </span>
                </div>

                {version.change_summary && (
                  <p className="text-sm text-gray-700 mb-3">
                    {version.change_summary}
                  </p>
                )}

                {version.content_diff && (
                  <details className="mb-3">
                    <summary className="cursor-pointer text-sm text-blue-600 hover:text-blue-800">
                      View Changes
                    </summary>
                    <pre className="mt-2 p-3 bg-gray-50 rounded text-xs text-gray-700 overflow-x-auto max-h-32">
                      {version.content_diff}
                    </pre>
                  </details>
                )}
              </div>

              <div className="flex space-x-2 ml-4">
                <button
                  onClick={() =>
                    setSelectedVersion(
                      selectedVersion?.id === version.id ? null : version
                    )
                  }
                  className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
                >
                  <Eye className="w-3 h-3" />
                  <span>Preview</span>
                </button>

                {version.version_number !== versionHistory.current_version && (
                  <button
                    onClick={() => handleRollback(version.version_number)}
                    disabled={rollbackLoading === version.version_number}
                    className="flex items-center space-x-1 px-3 py-1 text-sm text-orange-600 hover:bg-orange-50 rounded disabled:opacity-50"
                  >
                    {rollbackLoading === version.version_number ? (
                      <LoadingIndicator isLoading={true} size="sm" />
                    ) : (
                      <RotateCcw className="w-3 h-3" />
                    )}
                    <span>Rollback</span>
                  </button>
                )}
              </div>
            </div>

            {/* Content Preview */}
            {selectedVersion?.id === version.id && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-900 mb-2">
                  Content Preview
                </h4>
                <div className="bg-gray-50 rounded p-3 max-h-64 overflow-y-auto">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                    {version.content_snapshot}
                  </pre>
                </div>
              </div>
            )}
          </div>
        ))}

        {versionHistory?.versions.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <History className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No version history available</p>
            <p className="text-sm">
              Versions will appear here as the document is modified
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
