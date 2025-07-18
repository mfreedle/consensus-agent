#!/usr/bin/env python3
"""Debug script to check Google OAuth configuration"""

import os
import sys

# Add current directory to path to import app modules
sys.path.append('.')

from app.config import settings


def main():
    print("Google OAuth Configuration Debug")
    print("=" * 40)
    print(f"App Environment: {settings.app_env}")
    print(f"CORS Origins: {settings.cors_origins}")
    print(f"Google Client ID: {settings.google_client_id[:20]}..." if settings.google_client_id else "Not set")
    print(f"Google Client Secret: {'Set' if settings.google_client_secret else 'Not set'}")
    print(f"Google Redirect URI (env): {settings.google_redirect_uri}")
    print(f"Google Redirect URI (resolved): {settings.google_redirect_uri_resolved}")
    print()
    print("Environment Variables:")
    print(f"GOOGLE_CLIENT_ID: {'Set' if os.getenv('GOOGLE_CLIENT_ID') else 'Not set'}")
    print(f"GOOGLE_CLIENT_SECRET: {'Set' if os.getenv('GOOGLE_CLIENT_SECRET') else 'Not set'}")
    print(f"GOOGLE_REDIRECT_URI: {os.getenv('GOOGLE_REDIRECT_URI', 'Not set')}")
    print(f"APP_ENV: {os.getenv('APP_ENV', 'Not set')}")
    print(f"CORS_ORIGINS: {os.getenv('CORS_ORIGINS', 'Not set')}")
    print(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not set')}")
    print(f"RAILWAY_STATIC_URL: {os.getenv('RAILWAY_STATIC_URL', 'Not set')}")
    print(f"RAILWAY_PUBLIC_DOMAIN: {os.getenv('RAILWAY_PUBLIC_DOMAIN', 'Not set')}")

if __name__ == "__main__":
    main()
