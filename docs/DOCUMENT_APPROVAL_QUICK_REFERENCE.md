# Document Approval Workflow - Quick Reference

## 🚀 Quick Actions

| Action             | Steps                                                     |
| ------------------ | --------------------------------------------------------- |
| **Review Pending** | Sidebar → Approvals → Click "Review"                      |
| **Approve/Reject** | Open approval → Review diff → Click "Approve" or "Reject" |
| **View History**   | Approvals → "History" tab                                 |
| **Apply Changes**  | History tab → Click "Apply Changes"                       |
| **Upload Files**   | Sidebar → Files → Drag & drop or click "Choose File"      |

## 📋 Dashboard Overview

### Pending Approvals Tab
- **Status Badge**: Shows current approval state
- **Time Remaining**: Countdown before expiration  
- **File Info**: Document name and change type
- **AI Reasoning**: Confidence score and explanation
- **Actions**: Review, Approve, Reject buttons

### History Tab
- **All Statuses**: Pending, Approved, Rejected
- **Applied Status**: Shows if changes are live
- **Apply Button**: For approved but not applied items

## 🔍 Review Process

### 1. Open Approval
Click "Review" → Detailed view opens

### 2. Analyze Content
- **Left Panel**: Approval info, AI reasoning
- **Right Panel**: Side-by-side content diff
- **Original**: Current document content
- **Proposed**: Suggested changes (highlighted)

### 3. Make Decision
- ✅ **Approve**: Changes look good
- ❌ **Reject**: Changes need revision
- ⬅️ **Back**: Return without deciding

## 💡 Best Practices

### ✅ Do
- Read AI reasoning before deciding
- Check confidence scores (80%+ is good)
- Review full context of changes
- Act before expiration (24 hours)
- Apply approved changes promptly

### ❌ Don't
- Ignore AI confidence scores
- Rush through complex changes
- Skip reviewing diff content
- Let approvals expire unnecessarily

## 🎯 Use Case Examples

### Content Updates
**Scenario**: Blog post improvement  
**Action**: Review AI suggestions for readability  
**Decision**: Approve if changes enhance clarity

### Documentation
**Scenario**: API docs update  
**Action**: Verify technical accuracy  
**Decision**: Approve if information is correct

### Marketing Materials
**Scenario**: Email template optimization  
**Action**: Check brand consistency  
**Decision**: Approve if messaging aligns

## 🔧 Troubleshooting

| Problem             | Solution                                   |
| ------------------- | ------------------------------------------ |
| No pending items    | Check Files tab - upload documents first   |
| Can't approve       | Verify approval hasn't expired             |
| Changes not applied | Look for "Apply Changes" button in History |
| Diff not showing    | Check file format is supported             |

## 📁 Supported File Types

**Supported**: PDF, DOCX, TXT, MD, XLSX, CSV, PPTX  
**Limits**: 5 files max, 50MB each

## ⏰ Important Timings

- **Expiration**: 24 hours from creation
- **Processing**: Real-time status updates
- **History**: Permanent record of all decisions

## 🆘 Need Help?

1. Check main user guide: `DOCUMENT_APPROVAL_WORKFLOW_USER_GUIDE.md`
2. Review API documentation for technical details
3. Contact system administrator for permissions

---
**Quick Tip**: Use the confidence score as a guide - higher scores (85%+) typically indicate more reliable AI suggestions!
