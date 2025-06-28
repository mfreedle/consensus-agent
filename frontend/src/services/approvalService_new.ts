import { EnhancedApiService } from './enhancedApi';

export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'expired';

export type ChangeType = 'content_edit' | 'content_append' | 'content_insert' | 
                        'content_delete' | 'formatting_change' | 'metadata_update';

export interface DocumentApproval {
  id: number;
  file_id: number;
  chat_session_id?: number;
  title: string;
  description?: string;
  change_type: ChangeType;
  original_content?: string;
  proposed_content: string;
  change_location?: Record<string, any>;
  change_metadata?: Record<string, any>;
  ai_reasoning?: string;
  confidence_score?: number;
  status: ApprovalStatus;
  approved_at?: string;
  approved_by_user: boolean;
  expires_at?: string;
  version_before?: string;
  version_after?: string;
  is_applied: boolean;
  applied_at?: string;
  application_error?: string;
  created_at: string;
  updated_at?: string;
  file_name?: string;
  chat_session_title?: string;
}

export interface CreateApprovalRequest {
  file_id: number;
  chat_session_id?: number;
  title: string;
  description?: string;
  change_type: ChangeType;
  original_content?: string;
  proposed_content: string;
  change_location?: Record<string, any>;
  change_metadata?: Record<string, any>;
  ai_reasoning?: string;
  confidence_score?: number;
  expires_in_hours?: number;
}

export interface ApprovalDecision {
  decision: 'approved' | 'rejected';
  reason?: string;
}

export interface ContentDiff {
  original_lines: string[];
  proposed_lines: string[];
  diff_html: string;
  diff_text: string;
  change_summary: string;
  lines_added: number;
  lines_removed: number;
  lines_modified: number;
}

export interface DocumentVersion {
  id: number;
  file_id: number;
  version_hash: string;
  version_number: number;
  content_snapshot: string;
  content_diff?: string;
  change_summary?: string;
  file_size?: number;
  file_metadata?: Record<string, any>;
  created_at: string;
}

export interface VersionHistory {
  file_id: number;
  file_name: string;
  current_version: number;
  total_versions: number;
  versions: DocumentVersion[];
}

class DocumentApprovalService {
  private api: EnhancedApiService;

  constructor() {
    this.api = new EnhancedApiService();
  }

  /**
   * Create a new document approval request
   */
  async createApproval(request: CreateApprovalRequest): Promise<DocumentApproval> {
    return this.api.request<DocumentApproval>('/files/approvals', {
      method: 'POST',
      body: JSON.stringify(request),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Get pending approval requests
   */
  async getPendingApprovals(limit: number = 20): Promise<DocumentApproval[]> {
    return this.api.request<DocumentApproval[]>(`/files/approvals/pending?limit=${limit}`, {
      method: 'GET',
    });
  }

  /**
   * Get approval history
   */
  async getApprovalHistory(limit: number = 50): Promise<DocumentApproval[]> {
    return this.api.request<DocumentApproval[]>(`/files/approvals/history?limit=${limit}`, {
      method: 'GET',
    });
  }

  /**
   * Process approval decision (approve or reject)
   */
  async processApprovalDecision(
    approvalId: number, 
    decision: ApprovalDecision
  ): Promise<DocumentApproval> {
    return this.api.request<DocumentApproval>(
      `/files/approvals/${approvalId}/decision`,
      {
        method: 'POST',
        body: JSON.stringify(decision),
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }

  /**
   * Get content diff for an approval request
   */
  async getApprovalDiff(approvalId: number): Promise<ContentDiff> {
    return this.api.request<ContentDiff>(`/files/approvals/${approvalId}/diff`, {
      method: 'GET',
    });
  }

  /**
   * Rollback file to a specific version
   */
  async rollbackFileVersion(fileId: number, versionNumber: number): Promise<any> {
    return this.api.request<any>(
      `/files/${fileId}/rollback/${versionNumber}`,
      {
        method: 'POST',
      }
    );
  }

  /**
   * Get version history for a file
   */
  async getFileVersionHistory(fileId: number): Promise<VersionHistory> {
    return this.api.request<VersionHistory>(`/files/${fileId}/versions`, {
      method: 'GET',
    });
  }

  /**
   * Expire old pending approvals (maintenance)
   */
  async expireOldApprovals(): Promise<any> {
    return this.api.request<any>('/files/maintenance/expire-approvals', {
      method: 'POST',
    });
  }

  /**
   * Helper: Format approval status for display
   */
  formatStatus(status: ApprovalStatus): string {
    const statusMap: Record<ApprovalStatus, string> = {
      pending: 'Pending Review',
      approved: 'Approved',
      rejected: 'Rejected',
      expired: 'Expired'
    };
    return statusMap[status] || status;
  }

  /**
   * Helper: Format change type for display
   */
  formatChangeType(changeType: ChangeType): string {
    const typeMap: Record<ChangeType, string> = {
      content_edit: 'Content Edit',
      content_append: 'Content Append',
      content_insert: 'Content Insert',
      content_delete: 'Content Delete',
      formatting_change: 'Formatting Change',
      metadata_update: 'Metadata Update'
    };
    return typeMap[changeType] || changeType;
  }

  /**
   * Helper: Get status color for UI
   */
  getStatusColor(status: ApprovalStatus): string {
    const colorMap: Record<ApprovalStatus, string> = {
      pending: 'text-yellow-600 bg-yellow-50',
      approved: 'text-green-600 bg-green-50',
      rejected: 'text-red-600 bg-red-50',
      expired: 'text-gray-600 bg-gray-50'
    };
    return colorMap[status] || 'text-gray-600 bg-gray-50';
  }

  /**
   * Helper: Check if approval is actionable (can be approved/rejected)
   */
  isActionable(approval: DocumentApproval): boolean {
    return approval.status === 'pending' && 
           (!approval.expires_at || new Date(approval.expires_at) > new Date());
  }

  /**
   * Helper: Calculate time remaining for approval
   */
  getTimeRemaining(approval: DocumentApproval): string | null {
    if (!approval.expires_at) return null;
    
    const now = new Date();
    const expires = new Date(approval.expires_at);
    const diff = expires.getTime() - now.getTime();
    
    if (diff <= 0) return 'Expired';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days} day(s) remaining`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m remaining`;
    } else {
      return `${minutes}m remaining`;
    }
  }
}

export const approvalService = new DocumentApprovalService();
