#!/bin/bash
# Open WebUI startup script with automatic OAuth callback deployment

echo "🚀 Starting Open WebUI with automatic OAuth deployment..."

# Deploy OAuth callback page on startup
echo "📋 Deploying OAuth callback page..."

# Ensure the static directory exists
mkdir -p /app/build

# Deploy OAuth callback page from image (copied in Dockerfile)
echo "Deploying OAuth callback page from image..."
if [ -f "/app/google-oauth-callback.html" ]; then
    cp /app/google-oauth-callback.html /app/build/google-oauth-callback.html
    echo "✅ OAuth callback page deployed successfully from image!"
    echo "📍 Available at: /google-oauth-callback.html"
    echo "📁 File size: $(stat -c%s /app/build/google-oauth-callback.html) bytes"
else
    echo "❌ OAuth callback page not found in image at /app/google-oauth-callback.html"
fi

# Fallback: Check if callback page exists in data/opt and copy it
if [ ! -f "/app/build/google-oauth-callback.html" ] && [ -f "/app/backend/data/opt/google-oauth-callback.html" ]; then
    cp /app/backend/data/opt/google-oauth-callback.html /app/build/google-oauth-callback.html
    echo "✅ OAuth callback page deployed successfully from data/opt fallback!"
    echo "📍 Available at: /google-oauth-callback.html"
elif [ ! -f "/app/build/google-oauth-callback.html" ]; then
    echo "⚠️  OAuth callback page not found in either location"
    echo "📝 This is normal for first-time setup - callback will be available once tools are loaded"
fi

# Ensure proper permissions
chmod 644 /app/build/google-oauth-callback.html 2>/dev/null || true

# Create data directories
echo "Creating data directories..."
mkdir -p /app/backend/data/opt/tokens

echo "🎯 OAuth deployment complete, starting Open WebUI..."
echo "🌐 OAuth callback will be available at: http://localhost:8080/google-oauth-callback.html"
echo ""

# Start Open WebUI with the original command
exec bash start.sh
