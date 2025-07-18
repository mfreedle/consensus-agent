#!/usr/bin/env python3
"""Test Google OAuth URL generation"""

import os
import sys

# Add current directory to path to import app modules
sys.path.append('.')

from app.config import settings
from app.google.service import GoogleDriveService


def main():
    print("Testing Google OAuth URL Generation")
    print("=" * 40)
    
    # Create Google service instance
    google_service = GoogleDriveService(settings)
    
    try:
        # Generate authorization URL
        auth_url, state = google_service.get_authorization_url("test-state")
        
        print("✅ Successfully generated OAuth URL")
        print(f"Auth URL: {auth_url[:100]}...")
        print(f"State: {state}")
        print(f"Redirect URI used: {settings.google_redirect_uri_resolved}")
        
    except Exception as e:
        print(f"❌ Error generating OAuth URL: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
