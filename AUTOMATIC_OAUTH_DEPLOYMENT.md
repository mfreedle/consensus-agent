# Automatic OAuth Callback Deployment

This document explains how to automatically deploy the OAuth callback page on container startup using different approaches.

## � **Security Setup (REQUIRED FIRST)**

Before using any deployment option, set up your environment variables securely:

### 1. Create Environment File

```bash
# Copy the template
cp .env.template .env

# Edit with your actual credentials
# NEVER commit .env to Git!
```

### 2. Set Your Credentials in .env

```bash
GOOGLE_DRIVE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_DRIVE_API_KEY=your-api-key
GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:19328/google-oauth-callback.html
WEBUI_SECRET_KEY=your-random-secret-key
```

### 3. For Railway Deployment

Set environment variables in Railway dashboard instead of using .env file.

---

## �🚀 **Option 1: Dockerfile with Custom Startup Script (Recommended)**

**Files**: `Dockerfile`, `startup.sh`

**How it works**:

- Custom startup script `startup.sh` runs on container start
- Automatically copies OAuth callback page to `/app/build/`
- Then starts Open WebUI normally

**Usage**:

```bash
# Build and run with automatic OAuth deployment
docker-compose up --build

# OAuth callback automatically available at:
# http://localhost:19328/google-oauth-callback.html
```

**Pros**:

- ✅ Works with any deployment (Docker Compose, Railway, etc.)
- ✅ Self-contained in the Docker image
- ✅ No volume mounting required for the script

**Cons**:

- ⚠️ Requires rebuilding image when script changes

---

## 🔧 **Option 2: Docker Compose Entrypoint Override**

**Files**: `docker-compose-entrypoint-oauth.yml`

**How it works**:

- Overrides the container entrypoint via docker-compose
- Mounts the OAuth deployment script as a volume
- Runs deployment script before starting Open WebUI

**Usage**:

```bash
# First: Set up your .env file (see Security Setup above)
cp .env.template .env
# Edit .env with your credentials

# Use the custom docker-compose file
docker-compose -f docker-compose-entrypoint-oauth.yml up --build
```

**Pros**:

- ✅ No Dockerfile changes needed
- ✅ Script changes don't require image rebuild
- ✅ Easy to enable/disable

**Cons**:

- ⚠️ Requires specific docker-compose file
- ⚠️ Script must be available on host for volume mount

---

## 🎯 **Option 3: Init Container Pattern**

**Files**: Could be implemented with separate init container

**How it works**:

- Separate init container runs deployment script
- Main container starts after init completes
- Shared volume for static files

**Usage**: (Not implemented yet)

```bash
# Would need separate init container definition
docker-compose up --build
```

**Pros**:

- ✅ Clean separation of concerns
- ✅ Can run complex setup tasks

**Cons**:

- ⚠️ More complex setup
- ⚠️ Additional container overhead

---

## 📊 **Comparison & Recommendation**

| Feature                | Dockerfile Startup | Compose Entrypoint | Init Container |
| ---------------------- | ------------------ | ------------------ | -------------- |
| **Simplicity**         | ⭐⭐⭐⭐⭐         | ⭐⭐⭐⭐           | ⭐⭐⭐         |
| **Flexibility**        | ⭐⭐⭐             | ⭐⭐⭐⭐⭐         | ⭐⭐⭐⭐       |
| **Railway Compatible** | ⭐⭐⭐⭐⭐         | ⭐⭐⭐             | ⭐⭐⭐⭐       |
| **Local Dev**          | ⭐⭐⭐⭐⭐         | ⭐⭐⭐⭐⭐         | ⭐⭐⭐⭐       |

### 🏆 **Recommended: Option 1 (Dockerfile Startup)**

**Reasons**:

- Works universally (local, Railway, any platform)
- Self-contained and reliable
- Simple to understand and maintain
- No external dependencies

---

## 🚨 **Current Implementation Status**

**Active**: Option 1 - Dockerfile with `startup.sh`

**Files Modified**:

- ✅ `Dockerfile` - Copies script and sets custom CMD
- ✅ `startup.sh` - Custom startup script with OAuth deployment
- ✅ `deploy_oauth_callback.sh` - Original deployment script (still usable manually)

**Test Commands**:

```bash
# Build and test locally
docker-compose up --build

# Check OAuth callback availability
curl -I "http://localhost:19328/google-oauth-callback.html"
# Should return: HTTP/1.1 200 OK

# Check startup logs
docker logs open-webui
# Should show: "✅ OAuth callback page deployed successfully!"
```

---

## 🔄 **Switching Between Options**

### To use Option 1 (Current):

```bash
# Use the updated Dockerfile
docker-compose up --build
```

### To use Option 2:

```bash
# Use the entrypoint override
docker-compose -f docker-compose-entrypoint-oauth.yml up --build
```

### To revert to manual deployment:

```bash
# Remove CMD override from Dockerfile and use original docker-compose.yml
docker-compose up --build
# Then manually run: docker exec open-webui /app/deploy_oauth_callback.sh
```

---

## 🎯 **Railway Deployment Notes**

For Railway deployment, Option 1 (Dockerfile startup) is the best choice because:

1. **No volume mounting needed** - Everything is self-contained
2. **Automatic OAuth deployment** - Works immediately on Railway startup
3. **Environment detection** - Automatically uses Railway domain for redirect URI
4. **Static file serving** - OAuth callback available at Railway domain

**Railway Environment Variables** (still needed):

```bash
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
RAILWAY_PUBLIC_DOMAIN=your-app.railway.app  # Auto-set by Railway
```

The OAuth callback will be automatically available at:
`https://your-app.railway.app/google-oauth-callback.html`
