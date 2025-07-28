# Google Workspace Tools - AI Assistant Integration Guide

## 🤖 **For AI Assistants: How to Handle User Requests**

### **Universal Entry Point**

For any user message, call this function first:

```python
handle_user_message(user_message)
```

This function automatically:

- ✅ Detects OAuth completion messages
- ✅ Processes natural language Google requests
- ✅ Provides appropriate guidance
- ✅ Returns empty string if not Google-related

### **Natural Language Patterns Supported**

#### **📁 Google Drive File Listing**

**User says:**

- "Show my Google Drive files"
- "List my Drive files"
- "What files are in my Google Drive?"
- "Browse my Drive"

**AI should call:** `show_my_drive_files(max_results=10)`

#### **📄 Document Creation**

**User says:**

- "Create a new document called 'My Report'"
- "Make a new Google Doc"
- "Create a document titled 'Meeting Notes'"

**AI should call:** `create_new_document(title, content="")`

#### **📊 Spreadsheet Creation**

**User says:**

- "Create a new spreadsheet called 'Budget 2025'"
- "Make a new Google Sheet"
- "Create a spreadsheet named 'Data Analysis'"

**AI should call:** `create_new_spreadsheet(title, data=None)`

#### **🔍 Drive Search**

**User says:**

- "Search my drive for 'budget'"
- "Find files containing 'report'"
- "Look for 'presentation' in my Drive"

**AI should call:** `search_my_drive(query, max_results=10)`

#### **🔧 Setup & Authentication**

**User says:**

- "Help me setup Google Workspace"
- "Connect to Google Drive"
- "How do I use Google tools?"

**AI should call:** `help_me_setup_google_workspace()`

#### **🔄 Reconnection**

**User says:**

- "Google Drive isn't working"
- "Reconnect to Google"
- "Fix my Google connection"

**AI should call:** `reconnect_to_google_drive()`

### **OAuth Completion Handling**

When user pastes OAuth completion messages like:

- "Complete authentication with code: 4/0AH..."
- "Authorization code: 4/0AH..."
- Direct OAuth codes

The `handle_user_message()` function automatically detects and processes them.

### **Authentication Flow**

1. **User requests Google action** → AI calls `handle_user_message()`
2. **If not authenticated** → Function automatically starts OAuth flow
3. **User completes OAuth** → Pastes completion message
4. **AI processes message** → `handle_user_message()` detects and completes setup
5. **User can now use Google tools** → All subsequent requests work seamlessly

### **Example AI Assistant Behavior**

```
User: "Show me my Google Drive files"

AI: [calls handle_user_message("Show me my Google Drive files")]

If not authenticated:
Response: "I'll help you access your Google Drive files! First, I need to set up
Google authentication for you... [OAuth URL provided]"

If authenticated:
Response: "📁 Your Google Drive Files (showing 10 files):
1. Budget 2025.xlsx (spreadsheet)
   Last modified: 2025-01-15
   [📂 Open in Google Drive](link)
..."
```

### **Error Handling**

All functions include automatic error handling and provide user-friendly messages for:

- ❌ Authentication failures
- ⚠️ Expired tokens
- 🔄 Connection issues
- 📝 Invalid requests

### **Production Deployment Notes**

For Railway/production deployment:

- Environment variables take precedence over credential files
- OAuth callback URLs automatically adjust to production domains
- All authentication state persists across sessions

### **Function Reference**

| User Intent        | Function to Call                      | Parameters              |
| ------------------ | ------------------------------------- | ----------------------- |
| Any Google request | `handle_user_message(message)`        | user's message          |
| Check auth status  | `authenticate_google_workspace()`     | none                    |
| List Drive files   | `show_my_drive_files(max_results)`    | number of files         |
| Create document    | `create_new_document(title, content)` | title, optional content |
| Create spreadsheet | `create_new_spreadsheet(title, data)` | title, optional data    |
| Search Drive       | `search_my_drive(query, max_results)` | search terms, number    |
| Setup help         | `help_me_setup_google_workspace()`    | none                    |
| Reconnect          | `reconnect_to_google_drive()`         | none                    |

### **Best Practices for AI Assistants**

1. **Always use `handle_user_message()` first** for any Google-related user input
2. **Let the functions handle authentication** - don't manually check auth status
3. **Trust the natural language processing** - it handles many variations
4. **Provide the full response** - functions return user-friendly formatted messages
5. **Don't expose technical function names** to users - speak naturally

This creates a seamless, production-ready Google Workspace integration that feels natural to users! 🚀
