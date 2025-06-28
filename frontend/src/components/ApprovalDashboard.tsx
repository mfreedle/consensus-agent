import React, { useState, useEffect, useCallback } from "react";
import {
  Clock,
  CheckCircle,
  XCircle,
  FileText,
  AlertCircle,
  Eye,
  History,
  Plus,
} from "lucide-react";
import LoadingIndicator from "./LoadingIndicator";
import {
  approvalService,
  DocumentApproval,
  ApprovalStatus,
} from "../services/approvalService";

interface ApprovalDashboardProps {
  onSelectApproval?: (approval: DocumentApproval) => void;
  onCreateApproval?: () => void;
}

export const ApprovalDashboard: React.FC<ApprovalDashboardProps> = ({
  onSelectApproval,
  onCreateApproval,
}) => {
  const [pendingApprovals, setPendingApprovals] = useState<DocumentApproval[]>(
    []
  );
  const [approvalHistory, setApprovalHistory] = useState<DocumentApproval[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<"pending" | "history">(
    "pending"
  );
  const [error, setError] = useState<string | null>(null);

  const handleError = (error: any, message: string) => {
    console.error(message, error);
    setError(message);
    // Clear error after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  const loadApprovals = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [pending, history] = await Promise.all([
        approvalService.getPendingApprovals(20),
        approvalService.getApprovalHistory(20),
      ]);
      setPendingApprovals(pending);
      setApprovalHistory(history);
    } catch (error) {
      handleError(error, "Failed to load approvals");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadApprovals();
  }, [loadApprovals]);

  const handleApprovalDecision = async (
    approval: DocumentApproval,
    decision: "approved" | "rejected",
    reason?: string
  ) => {
    try {
      await approvalService.processApprovalDecision(approval.id, {
        decision,
        reason,
      });

      // Refresh the lists
      await loadApprovals();
    } catch (error) {
      handleError(
        error,
        `Failed to ${decision === "approved" ? "approve" : "reject"} change`
      );
    }
  };

  const getStatusIcon = (status: ApprovalStatus) => {
    switch (status) {
      case "pending":
        return <Clock className="w-4 h-4 text-yellow-600" />;
      case "approved":
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case "rejected":
        return <XCircle className="w-4 h-4 text-red-600" />;
      case "expired":
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
      default:
        return <FileText className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const ApprovalCard: React.FC<{ approval: DocumentApproval }> = ({
    approval,
  }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getStatusIcon(approval.status)}
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${approvalService.getStatusColor(
              approval.status
            )}`}
          >
            {approvalService.formatStatus(approval.status)}
          </span>
        </div>
        <div className="text-sm text-gray-500">
          {formatDate(approval.created_at)}
        </div>
      </div>

      <h3 className="font-medium text-gray-900 mb-2">{approval.title}</h3>

      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
        <span className="flex items-center space-x-1">
          <FileText className="w-3 h-3" />
          <span>{approval.file_name || `File ${approval.file_id}`}</span>
        </span>
        <span className="px-2 py-1 bg-gray-100 rounded text-xs">
          {approvalService.formatChangeType(approval.change_type)}
        </span>
      </div>

      {approval.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {approval.description}
        </p>
      )}

      {approval.ai_reasoning && (
        <div className="bg-blue-50 border border-blue-200 rounded p-2 mb-3">
          <p className="text-xs text-blue-700">
            <strong>AI Reasoning:</strong> {approval.ai_reasoning}
          </p>
          {approval.confidence_score && (
            <p className="text-xs text-blue-600 mt-1">
              Confidence: {approval.confidence_score}%
            </p>
          )}
        </div>
      )}

      {approvalService.isActionable(approval) && (
        <div className="flex items-center justify-between">
          <div className="text-xs text-yellow-600">
            {approvalService.getTimeRemaining(approval)}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => onSelectApproval?.(approval)}
              className="flex items-center space-x-1 px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded"
            >
              <Eye className="w-3 h-3" />
              <span>Review</span>
            </button>
            <button
              onClick={() => handleApprovalDecision(approval, "approved")}
              className="flex items-center space-x-1 px-2 py-1 text-xs text-green-600 hover:bg-green-50 rounded"
            >
              <CheckCircle className="w-3 h-3" />
              <span>Approve</span>
            </button>
            <button
              onClick={() => handleApprovalDecision(approval, "rejected")}
              className="flex items-center space-x-1 px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded"
            >
              <XCircle className="w-3 h-3" />
              <span>Reject</span>
            </button>
          </div>
        </div>
      )}

      {!approvalService.isActionable(approval) &&
        approval.status === "pending" && (
          <div className="text-xs text-red-600">This approval has expired</div>
        )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingIndicator isLoading={true} size="lg" />
      </div>
    );
  }

  return (
    <div className="p-6">
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Document Approvals
        </h2>
        {onCreateApproval && (
          <button
            onClick={onCreateApproval}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Approval</span>
          </button>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-6">
        <button
          onClick={() => setSelectedTab("pending")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedTab === "pending"
              ? "bg-white text-blue-600 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>Pending ({pendingApprovals.length})</span>
        </button>
        <button
          onClick={() => setSelectedTab("history")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedTab === "history"
              ? "bg-white text-blue-600 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <History className="w-4 h-4" />
          <span>History</span>
        </button>
      </div>

      {/* Content */}
      {selectedTab === "pending" ? (
        <div className="space-y-4">
          {pendingApprovals.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No pending approvals</p>
              <p className="text-sm">
                Document changes will appear here for review
              </p>
            </div>
          ) : (
            pendingApprovals.map((approval) => (
              <ApprovalCard key={approval.id} approval={approval} />
            ))
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {approvalHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <History className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No approval history</p>
              <p className="text-sm">Past approvals will appear here</p>
            </div>
          ) : (
            approvalHistory.map((approval) => (
              <ApprovalCard key={approval.id} approval={approval} />
            ))
          )}
        </div>
      )}
    </div>
  );
};
