#!/usr/bin/env python3
"""
Test Google Workspace Tool Functions
Verify all functions are accessible and properly defined
"""

import os
import sys

# Add the data/opt directory to the path
sys.path.insert(0, os.path.dirname(__file__))


def test_tool_functions():
    """Test that all Google Workspace tool functions are accessible."""
    try:
        from google_workspace_tools_railway import Tools

        print("🔍 Testing Google Workspace Tool...")

        # Initialize the tool
        tools = Tools()
        print("✅ Tool initialized successfully")

        # Check that all expected functions exist
        expected_functions = [
            # Setup & Auth
            "authenticate_google_workspace",
            "get_oauth_authorization_url",
            "complete_oauth_setup",
            "help_me_setup_google_workspace",
            "what_google_workspace_tools_do_i_have",
            "quick_start_google_workspace",
            # Drive functions
            "show_my_drive_files",
            "search_my_drive",
            "search_google_drive",
            "list_google_drive_files",
            "create_google_doc",
            "create_google_sheet",
            "get_google_doc_content",
            # Gmail functions
            "list_gmail_messages",
            "send_gmail",
            "search_gmail",
            # Calendar functions
            "list_calendar_events",
            "create_calendar_event",
        ]

        missing_functions = []
        available_functions = []

        for func_name in expected_functions:
            if hasattr(tools, func_name) and callable(getattr(tools, func_name)):
                available_functions.append(func_name)
                print(f"✅ {func_name}")
            else:
                missing_functions.append(func_name)
                print(f"❌ {func_name} - MISSING")

        print("\n📊 Function Summary:")
        print(f"   Available: {len(available_functions)}")
        print(f"   Missing: {len(missing_functions)}")

        if missing_functions:
            print(f"\n❌ Missing functions: {missing_functions}")
            return False

        # Test the help function
        print("\n🧪 Testing help function...")
        help_result = tools.what_google_workspace_tools_do_i_have()
        print(f"✅ Help function works: {len(help_result)} characters")

        print(f"\n🎉 All {len(available_functions)} functions are available!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_tool_functions()
    sys.exit(0 if success else 1)
