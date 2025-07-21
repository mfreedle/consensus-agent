# Google Drive Integration Guide for LLM Agents

## 🎯 Overview
The Consensus Agent now has full Google Drive integration that allows LLM agents to create, read, and edit files on Google Drive when users have connected their Google account.

## 📋 Available Capabilities

### ✅ **File Creation**
LLM agents can create new files in the user's Google Drive:

#### 1. **Create Google Documents** 
- **Endpoint**: `POST /api/google/documents/create`
- **Purpose**: Create new Google Docs with content
- **Example Request**:
```json
{
  "title": "Meeting Notes - Project Discussion",
  "content": "## Meeting Summary\n\nDate: July 21, 2025\n\n### Key Points:\n- Project timeline approved\n- Budget allocation confirmed\n- Next steps defined",
  "folder_id": "optional_folder_id"
}
```

#### 2. **Create Google Spreadsheets**
- **Endpoint**: `POST /api/google/spreadsheets/create` 
- **Purpose**: Create new Google Sheets for data organization
- **Example Request**:
```json
{
  "title": "Project Budget Tracker",
  "folder_id": "optional_folder_id"
}
```

#### 3. **Create Google Presentations**
- **Endpoint**: `POST /api/google/presentations/create`
- **Purpose**: Create new Google Slides presentations
- **Example Request**:
```json
{
  "title": "Project Proposal Presentation",
  "folder_id": "optional_folder_id"
}
```

### ✅ **File Editing**
LLM agents can edit existing files:

#### 1. **Edit Any File Content**
- **Endpoint**: `POST /api/google/files/{file_id}/edit`
- **Purpose**: Update content of existing files
- **Example Request**:
```json
{
  "content": "Updated content for the document..."
}
```

#### 2. **Edit Spreadsheet Data**
- **Endpoint**: `POST /api/google/spreadsheets/{spreadsheet_id}/edit`
- **Purpose**: Update spreadsheet cells and data
- **Example Request**:
```json
{
  "range": "A1:B10",
  "values": [
    ["Name", "Amount"],
    ["Project A", "5000"],
    ["Project B", "7500"]
  ]
}
```

### ✅ **File Reading**
LLM agents can read file content:

#### 1. **Get File Content**
- **Endpoint**: `GET /api/google/files/{file_id}/content`
- **Purpose**: Read the content of any Google Drive file
- **Returns**: Full file content including text, formatting, etc.

#### 2. **List Files**
- **Endpoint**: `GET /api/google/files`
- **Purpose**: Browse user's Google Drive files
- **Query Parameters**:
  - `file_type`: Filter by file type (docs, sheets, slides, etc.)
  - `limit`: Limit number of results

### ✅ **File Management**
- **List folder contents**: Browse specific folders
- **Search files**: Find files by name or content
- **Get file metadata**: Access file properties and sharing settings

## 🔑 **Required Permissions**
The integration uses comprehensive OAuth scopes:

- `https://www.googleapis.com/auth/drive` - Full Google Drive access
- `https://www.googleapis.com/auth/documents` - Google Docs read/write
- `https://www.googleapis.com/auth/spreadsheets` - Google Sheets read/write  
- `https://www.googleapis.com/auth/presentations` - Google Slides read/write

## 🔄 **Authentication Flow**
1. User clicks "Connect to Google Drive" in the UI
2. OAuth popup opens for Google authentication
3. User grants permissions to the application
4. Google Drive is now accessible to LLM agents
5. Agents can create, read, and edit files seamlessly

## 💡 **Use Cases for LLM Agents**

### 📝 **Document Creation**
- Generate meeting notes and save to Google Docs
- Create project documentation
- Draft reports and proposals
- Generate formatted documents with rich content

### 📊 **Data Management** 
- Create budget trackers in Google Sheets
- Generate data analysis reports
- Build dashboards and charts
- Process and organize data from conversations

### 📋 **Presentation Building**
- Create slide decks for project proposals
- Generate training presentations
- Build data visualization slides
- Create executive summaries

### 🔄 **File Updates**
- Update existing documents with new information
- Append to meeting notes and logs
- Modify spreadsheets with fresh data
- Keep documentation current and accurate

## 🚀 **Implementation Status**
- ✅ Backend endpoints fully implemented
- ✅ Frontend API service methods available
- ✅ OAuth integration working
- ✅ File creation, editing, and reading operational
- ✅ Error handling and validation in place
- ✅ Comprehensive scopes and permissions configured

## 🎯 **Next Steps**
LLM agents can now use Google Drive integration to:
1. **Save conversation outputs** directly to Google Drive
2. **Create structured documents** from chat discussions  
3. **Update existing files** with new information
4. **Organize user data** in spreadsheets and presentations
5. **Provide rich, formatted outputs** beyond simple text responses

The Google Drive integration is fully operational and ready for LLM agent use!
