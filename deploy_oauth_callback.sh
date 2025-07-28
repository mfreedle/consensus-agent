#!/bin/bash
# Deploy OAuth callback page for Railway

echo "🚀 Deploying OAuth callback page..."

# Ensure the static directory exists
mkdir -p /app/build

# Copy the callback page to the static directory
cp /app/backend/data/opt/google-oauth-callback.html /app/build/google-oauth-callback.html

# Verify the copy
if [ -f "/app/build/google-oauth-callback.html" ]; then
    echo "✅ OAuth callback page deployed successfully!"
    echo "📍 Available at: <your-railway-domain>/google-oauth-callback.html"
else
    echo "❌ Failed to deploy OAuth callback page"
fi

# Test if Open WebUI is serving static files
echo "🔍 Testing static file access..."
curl -I "http://localhost:8080/google-oauth-callback.html" 2>/dev/null || echo "⚠️  Local test failed - check Open WebUI static serving"
