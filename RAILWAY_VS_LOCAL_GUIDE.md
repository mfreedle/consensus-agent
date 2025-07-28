# Railway vs Local Development Guide

## 🚀 Railway Deployment (Production)

Railway **only** uses these files:

- ✅ `Dockerfile` - Defines the container build
- ✅ `startup.sh` - Runs OAuth deployment + starts Open WebUI
- ✅ Environment variables set in Railway dashboard

**Railway ignores:**

- ❌ `docker-compose.yml` (in .gitignore)
- ❌ `.env` files (not used in Railway)

### Railway Environment Variables to Set:

```bash
GOOGLE_DRIVE_CLIENT_ID=your-client-id
GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://your-app.railway.app/google-oauth-callback.html
WEBUI_SECRET_KEY=your-secret-key
```

## 🏠 Local Development Options

### Option 1: Use Docker Compose (Recommended)

```bash
# Use the secure version with .env file
cp .env.template .env
# Edit .env with your credentials
docker-compose -f docker-compose.secure.yml up --build
```

### Option 2: Manual Docker Build (Exactly Like Railway)

```bash
# Build the same way Railway does
docker build -t open-webui-local .

# Run with environment variables (like Railway)
docker run -p 19328:8080 \
  -v ./data:/app/backend/data \
  -e GOOGLE_DRIVE_CLIENT_ID=your-client-id \
  -e GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret \
  -e GOOGLE_REDIRECT_URI=http://localhost:19328/google-oauth-callback.html \
  -e WEBUI_SECRET_KEY=your-secret-key \
  open-webui-local
```

## 🔄 Summary

- **Railway**: Uses `Dockerfile` + environment variables from dashboard
- **Local**: Use `docker-compose.secure.yml` + `.env` file
- **Automatic OAuth**: Works in both via `startup.sh` script in Dockerfile

**Key Point**: Railway completely ignores docker-compose files. The `docker-compose.secure.yml` is purely for local development convenience - Railway will never see or use it.
