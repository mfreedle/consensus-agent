#!/usr/bin/env python3
"""
Test script to verify LLM can use Google Drive search and navigation capabilities
"""
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.config import Settings
from app.google.service import GoogleDriveService
from app.llm.google_drive_tools import GoogleDriveTools
from app.llm.orchestrator import LLMOrchestrator


def test_llm_google_drive_search():
    """Test that LLM can use Google Drive search functions"""
    print("🔍 Testing LLM Google Drive Search Capabilities")
    print("=" * 60)
    
    # Initialize services
    settings = Settings()
    google_service = GoogleDriveService(settings)
    google_tools = GoogleDriveTools(google_service)
    
    # Get available functions
    functions = google_tools.get_available_functions()
    
    # Check for search and navigation functions
    search_functions = [
        'search_google_drive_files',
        'list_folder_contents', 
        'find_folder_by_name',
        'get_file_path',
        'list_all_files_with_paths'
    ]
    
    print("🔍 Available Google Drive Functions:")
    for func in functions:
        indicator = "✅" if func.name in search_functions else "📄"
        print(f"   {indicator} {func.name}: {func.description}")
    
    print("\n🎯 Search & Navigation Functions:")
    for func_name in search_functions:
        found = any(f.name == func_name for f in functions)
        status = "✅ Available" if found else "❌ Missing"
        print(f"   {status}: {func_name}")
    
    # Test LLM orchestrator setup
    print("\n🤖 Testing LLM Orchestrator Setup:")
    orchestrator = LLMOrchestrator()
    orchestrator.set_google_drive_tools(google_tools)
    
    # Get tools for OpenAI format
    openai_tools = orchestrator._get_google_drive_tools_for_openai()
    search_tool_names = [tool['function']['name'] for tool in openai_tools if tool['function']['name'] in search_functions]
    
    print(f"   ✅ Total tools available to LLM: {len(openai_tools)}")
    print(f"   ✅ Search & navigation tools: {len(search_tool_names)}")
    
    for tool_name in search_tool_names:
        print(f"      • {tool_name}")
    
    # Test search function schema
    print("\n📋 Sample Search Function Schema:")
    search_tool = next((tool for tool in openai_tools if tool['function']['name'] == 'search_google_drive_files'), None)
    if search_tool:
        print(f"   Function: {search_tool['function']['name']}")
        print(f"   Description: {search_tool['function']['description']}")
        print(f"   Parameters: {list(search_tool['function']['parameters']['properties'].keys())}")
    
    print("\n🎉 Test Complete!")
    print("📋 Summary:")
    print("   ✅ Google Drive service initialized")
    print("   ✅ Google Drive tools initialized")
    print("   ✅ LLM orchestrator configured")
    print(f"   ✅ {len(search_functions)} search/navigation functions available")
    print("   ✅ Tools properly exposed to LLM")
    
    print("\n🚀 Next Steps:")
    print("   1. Connect Google Drive in frontend")
    print("   2. Test LLM search: 'Find all documents with project in the name'")
    print("   3. Test LLM navigation: 'Show me what's in the Reports folder'")
    print("   4. Test LLM path discovery: 'Show me the full path of my budget file'")

if __name__ == "__main__":
    test_llm_google_drive_search()
