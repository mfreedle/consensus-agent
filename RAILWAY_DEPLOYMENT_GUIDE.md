# Railway Deployment Guide for Open WebUI with Google Workspace Integration

## 📋 Railway Environment Variables Required

Set these environment variables in your Railway dashboard:

### Google OAuth Credentials

```bash
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_PROJECT_ID=your-project-id
```

### OpenAI API (Optional - Users can set their own)

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Railway-Specific Settings

```bash
# Update this with your actual Railway domain
GOOGLE_REDIRECT_URI=https://your-railway-app.railway.app/google-oauth-callback.html
```

## 🔧 Google Cloud Console Configuration

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project**: `your-project-id`
3. **Navigate to**: APIs & Services → Credentials
4. **Edit your OAuth 2.0 Client ID**
5. **Add Authorized Redirect URI**:
   ```
   https://your-railway-app.railway.app/google-oauth-callback.html
   ```

## 🚀 Railway Deployment Steps

### 1. Connect Repository to Railway

- Connect the `consensus-agent` repository
- Select the `open-webui-integration` branch
- Railway will auto-detect the Dockerfile

### 2. Set Environment Variables

In Railway dashboard → Settings → Variables, add all the environment variables listed above.

### 3. Deploy

Railway will automatically build and deploy your application.

### 4. Update OAuth Callback

Once deployed, update your `GOOGLE_REDIRECT_URI` environment variable with your actual Railway domain:

```bash
GOOGLE_REDIRECT_URI=https://consensus-agent-production.railway.app/google-oauth-callback.html
```

## 🧪 Testing the Deployment

1. **Access your Railway app**
2. **Install Google Workspace Tools**:
   - Go to Admin Panel → Tools
   - Upload the `google_workspace_tools.py` tool
3. **Test OAuth Flow**:
   - Use function calling: `authenticate_google_workspace()`
   - Follow the OAuth flow
   - Verify Google Drive integration works

## 🔄 Environment Variable Priority

The application supports both deployment methods:

1. **Production (Railway)**: Uses environment variables (preferred)
2. **Local Development**: Falls back to `oauth_credentials.json` file

## 📁 Files Not Needed in Production

These files are automatically ignored and don't need to be deployed:

- `data/opt/oauth_credentials.json` (replaced by env vars)
- `data/opt/tokens/` (will be created dynamically)
- Any local development files

## 🚨 Security Notes

- ✅ Credentials are stored as environment variables (secure)
- ✅ No sensitive files in the repository
- ✅ OAuth flow works with Railway's HTTPS endpoints
- ✅ Token storage is handled per-user automatically

## 🎯 Ready for Production!

Your Open WebUI application with Google Workspace integration is now ready for Railway deployment with enterprise-grade security practices!
