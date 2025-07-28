# Railway OAuth Callback Deployment

This script deploys the OAuth callback page for Railway:

## Quick Deployment

```bash
# Run inside Railway container
bash deploy_oauth_callback.sh
```

## Manual Steps

If automatic deployment doesn't work:

1. **Copy file manually:**

```bash
mkdir -p /app/build
cp /app/backend/data/opt/google-oauth-callback.html /app/build/google-oauth-callback.html
```

2. **Verify deployment:**

```bash
ls -la /app/build/google-oauth-callback.html
curl -I "https://your-railway-domain.railway.app/google-oauth-callback.html"
```

3. **Update Google Cloud Console redirect URI:**

```
https://your-railway-domain.railway.app/google-oauth-callback.html
```

## Troubleshooting

**Issue**: "Callback page not found"
**Solution**: Ensure Open WebUI serves static files from `/app/build/`

**Issue**: "redirect_uri_mismatch"  
**Solution**: Update Google Cloud Console with exact Railway URL

## Environment Variables Needed

```bash
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
GOOGLE_OAUTH_REDIRECT_URI=https://your-railway-domain.railway.app/google-oauth-callback.html
```
