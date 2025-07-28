# Railway Deployment with PostgreSQL Integration

## 🗄️ **Data Storage Strategy for Railway**

### **PostgreSQL Database (Structured Data)**

- User accounts and authentication
- Chat history and conversations
- Tool configurations and settings
- Application metadata

### **Railway Volumes (File Storage)**

- Google OAuth tokens (`/app/backend/data/opt/google_token.json`)
- Uploaded files (`/app/backend/data/uploads/`)
- Cached data (`/app/backend/data/cache/`)
- Vector database files (`/app/backend/data/vector_db/`)

## 🚀 **Railway Setup Steps**

### **1. Environment Variables in Railway**

Set these in Railway Dashboard → Settings → Variables:

```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_PROJECT_ID=

# Railway-specific URLs
GOOGLE_REDIRECT_URI=https://your-railway-app.railway.app/google-oauth-callback.html

# Security
WEBUI_SECRET_KEY=your-secure-secret-key-here

# Database (if using Railway PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Railway auto-populates this
```

### **2. PostgreSQL Service (Optional)**

If you want to use Railway's managed PostgreSQL:

1. **Add PostgreSQL Service** in Railway Dashboard
2. **Link to your app** - Railway will provide `DATABASE_URL`
3. **Configure Open WebUI** to use PostgreSQL instead of SQLite

### **3. Volume Persistence**

Railway automatically handles file persistence:

- No volume mounts needed in Railway
- Files in `/app/backend/data/` persist across deployments
- No configuration required

## 🔄 **Migration from Docker Compose**

### **Data Migration Strategy**

If you have existing data in your local `./data` folder:

1. **Export important data**:

   - Export user accounts/settings
   - Backup chat history
   - Save any custom configurations

2. **Deploy to Railway** with fresh start
3. **Re-import data** if needed
4. **Users re-authenticate** with Google (OAuth tokens are user-specific anyway)

### **Files That Transfer Automatically**

✅ Tool definitions (`data/opt/google_workspace_tools.py`)
✅ Static files and templates
✅ OAuth callback pages
✅ Configuration files (with placeholder credentials)

### **Files That Need Recreation**

🔄 OAuth tokens (users re-authenticate)
🔄 SQLite database (or migrate to PostgreSQL)
🔄 User-uploaded files (if any)
🔄 Cache files (regenerated automatically)

## ⚙️ **Open WebUI Configuration for Railway**

### **Database Configuration**

If using PostgreSQL, you may need to configure Open WebUI:

```python
# In Open WebUI settings or environment
DATABASE_URL=postgresql://user:pass@host:port/db
```

### **File Storage Paths**

These paths work the same on Railway:

- `/app/backend/data/opt/` - Tools and configurations
- `/app/backend/data/uploads/` - User uploads
- `/app/backend/data/cache/` - Temporary cache
- `/app/backend/data/vector_db/` - Vector database

## 🧪 **Testing Railway Deployment**

1. **Deploy without data** first
2. **Test basic functionality**
3. **Test Google OAuth flow** with Railway URLs
4. **Verify file uploads work**
5. **Test tool installation**
6. **Import any critical data**

## 🚨 **Important Notes**

### **Volume Size Limits**

Railway has volume size limits - monitor usage for:

- Large file uploads
- Vector database growth
- Cache accumulation

### **Database Choice**

- **SQLite**: Simpler, file-based (stored in Railway volume)
- **PostgreSQL**: More robust, managed by Railway, better for production

### **Environment Variables**

- Never put credentials in docker-compose.yml for Railway
- Use Railway's environment variable system
- Railway automatically encrypts and manages secrets

## ✅ **Summary**

**Local Docker Compose**: Uses `./data` volume mount
**Railway**: Uses automatic volume persistence + optional PostgreSQL

**Action Required**:

1. Set environment variables in Railway
2. Update OAuth redirect URI for Railway domain
3. Test deployment without local volume mounts
4. Users will re-authenticate (normal and expected)

Your Google Workspace tools will work perfectly on Railway with this configuration! 🚀
