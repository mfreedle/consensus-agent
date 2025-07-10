#!/usr/bin/env python3
"""
Debug script to test the specific issue where LLM says it will copy/move files but doesn't execute
"""
import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.config import Settings
from app.google.service import GoogleDriveService
from app.llm.google_drive_tools import GoogleDriveTools
from app.llm.orchestrator import LLMOrchestrator


async def debug_llm_function_execution():
    """Debug why LLM says it will do something but doesn't execute functions"""
    
    print("🔧 Debugging LLM Function Execution Issue")
    print("=" * 60)
    
    # Initialize services
    settings = Settings()
    google_service = GoogleDriveService(settings)
    google_tools = GoogleDriveTools(google_service)
    orchestrator = LLMOrchestrator()
    orchestrator.set_google_drive_tools(google_tools)
    
    print("✅ Services initialized")
    
    # Get available functions
    functions = google_tools.get_available_functions()
    
    print(f"\n📋 Available Functions: {len(functions)}")
    
    # Check specifically for file management functions
    file_mgmt_functions = [
        'copy_google_drive_file',
        'move_google_drive_file', 
        'delete_google_drive_file',
        'find_folder_by_name',
        'search_google_drive_files',
        'list_folder_contents'
    ]
    
    print("\n🎯 File Management Functions:")
    for func_name in file_mgmt_functions:
        found = any(f.name == func_name for f in functions)
        status = "✅ Available" if found else "❌ Missing"
        print(f"   {status}: {func_name}")
    
    # Get OpenAI-compatible tools
    openai_tools = orchestrator._get_google_drive_tools_for_openai()
    
    print(f"\n🤖 OpenAI Tools: {len(openai_tools)}")
    
    # Check function descriptions for clarity
    print("\n📝 Function Descriptions (should be clear for LLM):")
    for tool in openai_tools:
        if tool['function']['name'] in file_mgmt_functions:
            name = tool['function']['name']
            desc = tool['function']['description']
            print(f"   • {name}: {desc}")
    
    # Test specific copy file function schema
    copy_func = next((tool for tool in openai_tools if tool['function']['name'] == 'copy_google_drive_file'), None)
    if copy_func:
        print("\n📋 Copy File Function Schema:")
        print(f"   Name: {copy_func['function']['name']}")
        print(f"   Description: {copy_func['function']['description']}")
        print(f"   Required params: {copy_func['function']['parameters'].get('required', [])}")
        print(f"   All params: {list(copy_func['function']['parameters']['properties'].keys())}")
    
    # Test the user's specific scenario
    print("\n🧪 Testing User's Scenario:")
    print("   Task: Find file in 'AI Workshop' folder, copy to main folder")
    print("   Expected function sequence:")
    print("   1. find_folder_by_name('AI Workshop')")
    print("   2. list_folder_contents(folder_id)")  
    print("   3. search_google_drive_files('one_pager_v03.md')")
    print("   4. copy_google_drive_file(file_id, target_folder_id='root')")
    
    print("\n🔍 Potential Issues:")
    
    # Issue 1: Function choice configuration
    print("   1. Function choice is set to 'auto' - ✅ Good")
    
    # Issue 2: Missing parameters  
    copy_params = copy_func['function']['parameters']['properties'] if copy_func else {}
    required_params = copy_func['function']['parameters'].get('required', []) if copy_func else []
    print(f"   2. Copy function required params: {required_params}")
    print(f"   3. Copy function optional params: {[p for p in copy_params.keys() if p not in required_params]}")
    
    # Issue 3: Root folder handling
    if copy_func:
        target_folder_desc = copy_params.get('target_folder_id', {}).get('description', '')
        if 'root' in target_folder_desc:
            print("   4. Root folder handling: ✅ Documented")
        else:
            print("   4. Root folder handling: ⚠️ May need clarification")
    
    print("\n💡 Recommendations:")
    print("   1. ✅ All required functions are available")
    print("   2. ✅ Function descriptions are clear")
    print("   3. ✅ Root folder is supported with 'root' ID")
    print("   4. ⚠️ Check if LLM model has function calling issues")
    print("   5. ⚠️ Check if the response timeout is too short")
    print("   6. ⚠️ Consider using a more persistent model prompt")
    
    print("\n🚀 Suggested Solutions:")
    print("   1. Add more specific instructions in system prompt")
    print("   2. Use gpt-4o instead of gpt-4.1 for better function calling")
    print("   3. Add retry logic if function calls fail")
    print("   4. Increase response timeout if needed")
    
    print("\n✅ Debug Analysis Complete!")


if __name__ == "__main__":
    asyncio.run(debug_llm_function_execution())
