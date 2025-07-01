# Google Drive Integration Setup Guide

This guide explains how to set up Google Drive OAuth integration for the Consensus Agent application.

## Prerequisites

- A Google Cloud Console account
- Admin access to your Consensus Agent backend configuration

## Step 1: Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Drive API
   - Google Docs API
   - Google Sheets API (optional)
   - Google Slides API (optional)

## Step 2: Configure OAuth Consent Screen

1. In Google Cloud Console, go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace domain)
3. Fill in the required information:
   - App name: "Consensus Agent"
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes:
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/presentations`
5. Add test users (your email addresses) during development
   - <rthidden@gmail.com>

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Configure the OAuth client:
   - Name: "Consensus Agent Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:3010` (development)
     - `https://*.up.railway.app` (production)
   - Authorized redirect URIs:
     - `http://localhost:3010/google-oauth-callback.html` (development)
     - `https://*.up.railway.app/google-oauth-callback.html` (production)

### ⚠️ **IMPORTANT: What You Need After Step 3**

After creating the OAuth 2.0 Client ID, Google will provide you with these credentials:

1. **Client ID** (looks like: `123456789-abcdef.apps.googleusercontent.com`)
2. **Client Secret** (looks like: `GOCSPX-AbCdEf123456789`)

**These are the ONLY two credentials needed for the OAuth integration.**

You can find these credentials by:

- Going to "APIs & Services" > "Credentials" in Google Cloud Console
- Clicking on the OAuth 2.0 Client ID you just created
- The Client ID and Client Secret will be displayed

### 📝 **Service Account vs OAuth Credentials**

**You currently have Service Account credentials** (`gdrive_credentials.json`) which are different from OAuth credentials:

- **Service Account**: Used for server-to-server authentication (not needed for this integration)
- **OAuth 2.0**: Used for user authentication (required for this integration)

**You can keep both** - they serve different purposes and won't conflict.

## Step 4: Configure Backend Environment

1. Copy the `.env.example` file to `.env` in the backend directory
2. Add your Google OAuth credentials:

```env
# Google APIs - OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3010/google-oauth-callback.html
```

## Step 5: Test the Integration

1. Start the backend server:
   ```bash
   cd backend
   python dev.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. In the application:
   - Open the sidebar
   - Click on the "Drive" tab
   - Click "Connect Google Drive"
   - Complete the OAuth flow in the popup window

## Features Available After Setup

Once connected, users can:

- **View Google Drive Files**: Browse documents, spreadsheets, and presentations
- **Filter by File Type**: Show only Google Docs, Sheets, or Slides
- **Open Files**: Direct links to view/edit files in Google Drive
- **Read Document Content**: AI can access and analyze document content
- **Future Features**: Document editing and real-time collaboration

## Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch" Error**
   - Ensure the redirect URI in Google Cloud Console exactly matches the one in your `.env` file
   - Check for trailing slashes and protocol (http vs https)

2. **"Invalid Client" Error**
   - Verify your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
   - Make sure there are no extra spaces or characters

3. **Popup Blocked**
   - Allow popups for your domain in browser settings
   - Try using an incognito/private browsing window

4. **Scope Permissions Error**
   - Ensure all required scopes are added in Google Cloud Console
   - Check that the OAuth consent screen is properly configured

### Development vs Production

**Development:**
- Use `http://localhost:3010` for JavaScript origins
- Use test users for OAuth consent screen
- Keep app in "Testing" mode

**Production:**
- Use your actual domain for JavaScript origins
- Publish the OAuth consent screen for public use
- Update redirect URIs to use HTTPS

## Security Notes

- Store client secrets securely using environment variables
- Never commit credentials to version control
- Use HTTPS in production
- Regularly rotate OAuth client secrets
- Monitor API usage in Google Cloud Console

## API Rate Limits

Google Drive API has the following default quotas:
- 100,000,000 quota units per day
- 1,000 requests per 100 seconds per user

The integration is designed to be efficient and stay within these limits.
