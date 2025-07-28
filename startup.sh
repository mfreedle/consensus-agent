#!/bin/bash
# Open WebUI startup script with automatic OAuth callback deployment

echo "🚀 Starting Open WebUI with automatic OAuth deployment..."

# Deploy OAuth callback page on startup
echo "📋 Deploying OAuth callback page..."

# Ensure the static directory exists
mkdir -p /app/build

# Check if callback page exists in data/opt and copy it
if [ -f "/app/backend/data/opt/google-oauth-callback.html" ]; then
    cp /app/backend/data/opt/google-oauth-callback.html /app/build/google-oauth-callback.html
    echo "✅ OAuth callback page deployed successfully!"
    echo "📍 Available at: /google-oauth-callback.html"
else
    echo "⚠️  OAuth callback page not found at /app/backend/data/opt/google-oauth-callback.html"
    echo "📝 This is normal for first-time setup - callback will be available once tools are loaded"
fi

# Ensure proper permissions
chmod 644 /app/build/google-oauth-callback.html 2>/dev/null || true

echo "🎯 OAuth deployment complete, starting Open WebUI..."
echo "🌐 OAuth callback will be available at: http://localhost:8080/google-oauth-callback.html"
echo ""

# Start Open WebUI with the original command
exec bash start.sh
