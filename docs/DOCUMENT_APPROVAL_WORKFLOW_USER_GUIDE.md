# Document Approval Workflow - User Guide

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [User Stories & Use Cases](#user-stories--use-cases)
- [Step-by-Step Guide](#step-by-step-guide)
- [Features Overview](#features-overview)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Overview

The Document Approval Workflow in Consensus Agent provides a sophisticated system for collaborative document editing with AI-assisted change proposals and human approval processes. This workflow ensures that all document modifications go through a proper review process before being applied.

### Key Benefits
- **Quality Control**: Ensure all document changes are reviewed before implementation
- **Audit Trail**: Complete history of all document modifications and approvals
- **AI Integration**: Leverage AI reasoning to understand and evaluate proposed changes
- **Collaboration**: Enable team-based document review and approval processes
- **Version Control**: Track document versions and enable rollback capabilities

## Getting Started

### Prerequisites
1. Access to Consensus Agent application
2. Valid user account with authentication
3. Documents uploaded to the file system

### Quick Start
1. **Login** to Consensus Agent
2. **Upload documents** via the Files section
3. **Navigate** to the Approvals section in the sidebar
4. **Review pending approvals** or create new ones
5. **Make decisions** on approval requests
6. **Apply changes** to finalize document updates

## User Stories & Use Cases

### User Story 1: Content Manager - Blog Post Review
**As a** content manager  
**I want to** review AI-suggested improvements to blog posts  
**So that** I can ensure quality while leveraging AI assistance

**Scenario**: Sarah manages a company blog and receives AI-generated suggestions for improving existing posts.

**Example Workflow**:
1. AI analyzes a blog post about "Customer Success Stories"
2. AI suggests adding statistics and restructuring paragraphs for better flow
3. Sarah reviews the proposed changes in the approval interface
4. She sees the side-by-side comparison of original vs. proposed content
5. AI reasoning explains: "Added industry statistics to strengthen credibility and reorganized content for better narrative flow"
6. Sarah approves the changes and applies them to the live blog post

### User Story 2: Technical Writer - Documentation Updates
**As a** technical writer  
**I want to** manage updates to API documentation  
**So that** developers always have accurate information

**Scenario**: Mike maintains API documentation that needs regular updates when new features are released.

**Example Workflow**:
1. Development team releases new API endpoints
2. AI suggests updating the documentation with new endpoint descriptions
3. Mike receives an approval request for the documentation changes
4. He reviews the proposed additions and modifications
5. AI reasoning shows: "Added 3 new endpoints with proper examples and updated authentication section for clarity"
6. Mike approves with confidence score of 92%
7. Documentation is automatically updated

### User Story 3: Marketing Team - Campaign Material Review
**As a** marketing coordinator  
**I want to** review AI-suggested edits to campaign materials  
**So that** our messaging stays consistent and effective

**Scenario**: Lisa manages marketing campaigns and needs to review AI-suggested improvements to email templates.

**Example Workflow**:
1. AI analyzes email campaign performance data
2. AI suggests modifications to underperforming email templates
3. Lisa gets approval request with proposed subject line and body changes
4. She reviews A/B testing data and AI reasoning
5. AI explains: "Modified subject line for higher open rates and shortened body for better engagement based on performance data"
6. Lisa approves changes for the next campaign batch

### User Story 4: Legal Team - Contract Review
**As a** legal counsel  
**I want to** review AI-suggested contract modifications  
**So that** we maintain legal compliance while improving efficiency

**Scenario**: David reviews legal documents with AI assistance for standard contract improvements.

**Example Workflow**:
1. AI identifies opportunities to standardize contract language
2. AI proposes updates to liability clauses and termination conditions
3. David receives approval request with detailed change breakdown
4. He reviews each modification with legal implications in mind
5. AI provides reasoning: "Standardized liability language to match company policy and clarified termination procedures"
6. David approves after legal review and applies changes to template

## Step-by-Step Guide

### Accessing the Approval System

1. **Login to Consensus Agent**
   - Enter your username and password
   - Click "Sign In" to authenticate

2. **Navigate to Approvals**
   - Click the hamburger menu (☰) to open the sidebar
   - Click on "Approvals" tab in the navigation

### Reviewing Pending Approvals

3. **View Pending Items**
   - The dashboard shows all pending approval requests
   - Each item displays:
     - Status badge (Pending Review)
     - Timestamp of creation
     - Document title and description
     - File name and change type
     - AI reasoning and confidence score
     - Time remaining before expiration

4. **Open Detailed Review**
   - Click the "Review" button on any approval item
   - This opens the detailed ApprovalViewer interface

### Making Approval Decisions

5. **Analyze the Changes**
   - **Header Section**: Shows approval title, file info, and status
   - **Description**: Read the change description and context
   - **AI Reasoning**: Review AI's explanation and confidence score
   - **Document Changes**: Examine the side-by-side diff view
     - Left side: Original content
     - Right side: Proposed content
     - Changed sections are highlighted

6. **Make Your Decision**
   - **Approve**: Click "Approve" if changes look good
   - **Reject**: Click "Reject" if changes need revision
   - **Back to Dashboard**: Return without making a decision

### Managing Approved Changes

7. **View Approval History**
   - Click "History" tab to see all past decisions
   - Filter by status:
     - **Approved**: Changes that have been applied
     - **Pending Review**: Still awaiting decision
     - **Approved but not yet applied**: Requires manual application

8. **Apply Approved Changes**
   - For items showing "Apply Changes" button
   - Click the button to apply changes to the actual document
   - System will update the file and create a new version

### File Management Integration

9. **Upload and Manage Files**
   - Use the "Files" tab to upload documents
   - Supported formats: PDF, DOCX, TXT, MD, XLSX, CSV, PPTX
   - View, download, or delete files as needed
   - Files integrate with the approval workflow

### Creating New Approvals (Advanced)

10. **Manual Approval Creation**
    - Click "New Approval" button
    - Select target file
    - Provide change description
    - Submit for review

## Features Overview

### Dashboard Features
- **Pending Counter**: Shows number of items awaiting review
- **Quick Actions**: Review, Approve, Reject buttons
- **Status Indicators**: Visual badges for different approval states
- **Time Tracking**: Shows time remaining before expiration

### Review Interface Features
- **Side-by-Side Diff**: Compare original and proposed content
- **AI Insights**: Reasoning and confidence scoring
- **Metadata Display**: File information, change type, timestamps
- **Navigation**: Easy return to dashboard

### History Management
- **Complete Audit Trail**: All approval decisions tracked
- **Status Filtering**: View by approval state
- **Apply Controls**: Manual application of approved changes
- **Search and Sort**: Find specific approvals quickly

### File Integration
- **Multi-Format Support**: Wide range of document types
- **Version Tracking**: Automatic version creation
- **Drag & Drop Upload**: Easy file management
- **Processing Status**: Real-time upload and processing feedback

## Best Practices

### For Reviewers
1. **Read AI Reasoning**: Always review AI explanations before deciding
2. **Check Context**: Understand why changes are being suggested
3. **Verify Accuracy**: Ensure proposed changes maintain document integrity
4. **Consider Impact**: Think about how changes affect overall document purpose
5. **Act Promptly**: Review approvals before they expire

### For Content Quality
1. **Meaningful Descriptions**: Provide clear change descriptions
2. **Appropriate Confidence**: Pay attention to AI confidence scores
3. **Incremental Changes**: Prefer smaller, focused modifications
4. **Document Purpose**: Ensure changes align with document goals
5. **Consistency**: Maintain style and tone consistency

### For Team Collaboration
1. **Clear Communication**: Use descriptive titles and descriptions
2. **Timely Reviews**: Establish team SLAs for approval response times
3. **Escalation Process**: Define what to do for complex decisions
4. **Training**: Ensure team understands the approval workflow
5. **Documentation**: Keep records of approval criteria and standards

## Troubleshooting

### Common Issues

**Q: Approval request is not showing up**
- Check that you're in the correct tab (Pending vs History)
- Refresh the page or click "Refresh Files"
- Verify you have proper permissions for the file

**Q: Cannot approve or reject an item**
- Ensure the approval hasn't expired
- Check that you have appropriate user permissions
- Verify the approval is in "Pending Review" status

**Q: Changes not being applied after approval**
- Look for "Apply Changes" button in History tab
- Check if approval is in "Approved but not yet applied" status
- Manual application may be required for some changes

**Q: Diff view not showing properly**
- Ensure the document format is supported
- Check file integrity and processing status
- Try refreshing the approval view

### Error Messages

**"Approval request not found"**
- The approval may have been deleted or expired
- Check with system administrator

**"Changes have already been applied"**
- This approval has been processed and changes are live
- Check document version history for confirmation

**"Failed to process approval decision"**
- System error occurred during processing
- Try again or contact technical support

## FAQ

### General Questions

**Q: How long do approval requests stay active?**
A: Approval requests expire after 24 hours by default. Check the "remaining time" indicator on each item.

**Q: Can I modify an approval request after submission?**
A: No, approval requests are immutable once created. You would need to reject and create a new one.

**Q: What happens if I reject an approval?**
A: Rejected approvals are moved to history with "Rejected" status. No changes are applied to the document.

**Q: Can multiple people approve the same document?**
A: Currently, the system supports single-user approval per request. Team approval workflows may be added in future versions.

### Technical Questions

**Q: What file formats are supported?**
A: PDF, DOCX, TXT, MD, XLSX, CSV, PPTX files up to 50MB each.

**Q: How are document versions managed?**
A: Each approval creates a new document version with complete change tracking and rollback capabilities.

**Q: Is there an audit trail for approvals?**
A: Yes, complete history is maintained including who approved what and when.

**Q: Can I undo an applied approval?**
A: Use the file version history to rollback to previous versions if needed.

### AI and Automation

**Q: How accurate are AI suggestions?**
A: AI provides confidence scores with each suggestion. Higher scores (80%+) generally indicate more reliable suggestions.

**Q: Can I customize AI reasoning criteria?**
A: AI reasoning is currently system-generated based on content analysis. Customization options may be available in future updates.

**Q: What if AI suggests inappropriate changes?**
A: Always review and use human judgment. Reject any suggestions that don't meet your standards or requirements.

---

## Support

For additional help or feature requests:
- Check the main documentation in `/docs` folder
- Review the API documentation for technical integration
- Contact your system administrator for permissions issues

**Version**: 1.0  
**Last Updated**: June 28, 2025  
**Compatible with**: Consensus Agent v1.0+
