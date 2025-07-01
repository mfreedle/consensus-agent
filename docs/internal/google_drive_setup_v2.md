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