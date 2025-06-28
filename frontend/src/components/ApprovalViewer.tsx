import React, { useState, useEffect, useCallback } from "react";
import {
  CheckCircle,
  XCircle,
  FileText,
  Clock,
  ArrowLeft,
  Diff,
  AlertTriangle,
  Info,
} from "lucide-react";
import LoadingIndicator from "./LoadingIndicator";
import {
  approvalService,
  DocumentApproval,
  ContentDiff,
  ApprovalStatus,
} from "../services/approvalService";

interface ApprovalViewerProps {
  approval: DocumentApproval;
  onBack: () => void;
  onApprovalChange?: (updatedApproval: DocumentApproval) => void;
}

export const ApprovalViewer: React.FC<ApprovalViewerProps> = ({
  approval,
  onBack,
  onApprovalChange,
}) => {
  const [diff, setDiff] = useState<ContentDiff | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState("");
  const [showRejectForm, setShowRejectForm] = useState(false);

  const getDarkStatusColor = (status: ApprovalStatus): string => {
    const colorMap: Record<ApprovalStatus, string> = {
      pending: "text-yellow-400 bg-yellow-400/10 border border-yellow-400/20",
      approved: "text-green-400 bg-green-400/10 border border-green-400/20",
      rejected: "text-red-400 bg-red-400/10 border border-red-400/20",
      expired: "text-gray-400 bg-gray-400/10 border border-gray-400/20",
    };
    return (
      colorMap[status] ||
      "text-gray-400 bg-gray-400/10 border border-gray-400/20"
    );
  };

  const loadDiff = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const diffData = await approvalService.getApprovalDiff(approval.id);
      setDiff(diffData);
    } catch (error) {
      console.error("Failed to load diff:", error);
      setError("Failed to load document diff");
    } finally {
      setLoading(false);
    }
  }, [approval.id]);

  useEffect(() => {
    loadDiff();
  }, [loadDiff]);

  const handleApprove = async () => {
    try {
      setProcessing(true);
      const updatedApproval = await approvalService.processApprovalDecision(
        approval.id,
        { decision: "approved" }
      );
      onApprovalChange?.(updatedApproval);
    } catch (error) {
      console.error("Failed to approve:", error);
      setError("Failed to approve change");
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    try {
      setProcessing(true);
      const updatedApproval = await approvalService.processApprovalDecision(
        approval.id,
        {
          decision: "rejected",
          reason: rejectionReason || undefined,
        }
      );
      onApprovalChange?.(updatedApproval);
      setShowRejectForm(false);
      setRejectionReason("");
    } catch (error) {
      console.error("Failed to reject:", error);
      setError("Failed to reject change");
    } finally {
      setProcessing(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const isActionable = approvalService.isActionable(approval);

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-gray-400 hover:text-primary-cyan transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Approval Details */}
      <div className="bg-bg-dark-secondary border border-primary-teal/20 rounded-lg p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-xl font-semibold text-white mb-2">
              {approval.title}
            </h1>
            <div className="flex items-center space-x-4 text-sm text-gray-300">
              <span className="flex items-center space-x-1">
                <FileText className="w-4 h-4" />
                <span>{approval.file_name || `File ${approval.file_id}`}</span>
              </span>
              <span className="px-2 py-1 bg-primary-teal/20 rounded text-xs text-primary-cyan">
                {approvalService.formatChangeType(approval.change_type)}
              </span>
              <span className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>{formatDate(approval.created_at)}</span>
              </span>
            </div>
          </div>
          <span
            className={`px-3 py-1 text-sm font-medium rounded-full ${getDarkStatusColor(
              approval.status
            )}`}
          >
            {approvalService.formatStatus(approval.status)}
          </span>
        </div>

        {approval.description && (
          <div className="mb-4">
            <h3 className="text-sm font-medium text-white mb-2">Description</h3>
            <p className="text-gray-300">{approval.description}</p>
          </div>
        )}

        {approval.ai_reasoning && (
          <div className="bg-primary-blue/10 border border-primary-blue/20 rounded-lg p-4 mb-4">
            <div className="flex items-start space-x-2">
              <Info className="w-4 h-4 text-primary-blue mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-primary-blue mb-1">
                  AI Reasoning
                </h3>
                <p className="text-sm text-primary-cyan">
                  {approval.ai_reasoning}
                </p>
                {approval.confidence_score && (
                  <div className="mt-2">
                    <span className="text-xs text-primary-cyan">
                      Confidence: {approval.confidence_score}%
                    </span>
                    <div className="w-full bg-primary-teal/20 rounded-full h-2 mt-1">
                      <div
                        className="bg-primary-teal h-2 rounded-full transition-all duration-300"
                        style={{ width: `${approval.confidence_score}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {isActionable && (
          <div className="border-t pt-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-yellow-600">
                {approvalService.getTimeRemaining(approval)}
              </div>
              <div className="flex space-x-3">
                {!showRejectForm ? (
                  <>
                    <button
                      onClick={() => setShowRejectForm(true)}
                      disabled={processing}
                      className="flex items-center space-x-2 px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 disabled:opacity-50"
                    >
                      <XCircle className="w-4 h-4" />
                      <span>Reject</span>
                    </button>
                    <button
                      onClick={handleApprove}
                      disabled={processing}
                      className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      <CheckCircle className="w-4 h-4" />
                      <span>Approve</span>
                    </button>
                  </>
                ) : (
                  <div className="flex items-center space-x-3">
                    <input
                      type="text"
                      placeholder="Reason for rejection (optional)"
                      value={rejectionReason}
                      onChange={(e) => setRejectionReason(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={() => {
                        setShowRejectForm(false);
                        setRejectionReason("");
                      }}
                      className="px-3 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleReject}
                      disabled={processing}
                      className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                    >
                      <XCircle className="w-4 h-4" />
                      <span>Confirm Reject</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Content Diff */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Diff className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Document Changes
          </h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <LoadingIndicator isLoading={true} size="md" />
          </div>
        ) : diff ? (
          <div>
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">
                {diff.change_summary}
              </p>
              <div className="flex space-x-4 text-xs text-gray-600">
                {diff.lines_added > 0 && (
                  <span className="text-green-600">
                    +{diff.lines_added} lines added
                  </span>
                )}
                {diff.lines_removed > 0 && (
                  <span className="text-red-600">
                    -{diff.lines_removed} lines removed
                  </span>
                )}
                {diff.lines_modified > 0 && (
                  <span className="text-blue-600">
                    {diff.lines_modified} lines modified
                  </span>
                )}
              </div>
            </div>

            {/* Simple text diff display */}
            <div className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">
                    Original
                  </h3>
                  <pre className="text-sm text-gray-700 bg-white p-3 rounded border max-h-64 overflow-y-auto">
                    {diff.original_lines.join("\n")}
                  </pre>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">
                    Proposed
                  </h3>
                  <pre className="text-sm text-gray-700 bg-white p-3 rounded border max-h-64 overflow-y-auto">
                    {diff.proposed_lines.join("\n")}
                  </pre>
                </div>
              </div>
            </div>

            {diff.diff_text && (
              <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                  View Unified Diff
                </summary>
                <pre className="mt-2 p-3 bg-gray-50 rounded text-xs text-gray-700 overflow-x-auto">
                  {diff.diff_text}
                </pre>
              </details>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Diff className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>Unable to load document diff</p>
          </div>
        )}
      </div>

      {processing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
            <LoadingIndicator isLoading={true} size="md" />
            <span>Processing approval...</span>
          </div>
        </div>
      )}
    </div>
  );
};
