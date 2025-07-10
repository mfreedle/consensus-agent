import sys
sys.path.append('.')
from app.llm.orchestrator import LLMOrchestrator
from app.llm.google_drive_tools import GoogleDriveTools
from app.google.service import GoogleDriveService
from app.config import settings
import json

# Initialize orchestrator
orchestrator = LLMOrchestrator()

# Setup Google Drive tools
google_service = GoogleDriveService(settings)
google_drive_tools = GoogleDriveTools(google_service)
orchestrator.set_google_drive_tools(google_drive_tools)

# Get tools for Responses API
tools = orchestrator._get_google_drive_tools_for_responses_api()

print('=== OpenAI Responses API Tool Format ===')
print(f'Number of tools: {len(tools)}')
print()

for i, tool in enumerate(tools):
    print(f'Tool {i + 1}: {tool.get(\"name\", \"UNKNOWN\")}')
    print('Schema:')
    print(json.dumps(tool, indent=2))
    print()
    
    # Check required fields
    required_fields = ['type', 'name', 'parameters', 'strict']
    missing_fields = [field for field in required_fields if field not in tool]
    
    if missing_fields:
        print(f'❌ Tool missing required fields: {missing_fields}')
    else:
        print(f'✅ Tool has all required fields')
        
        # Check field types
        if tool['type'] != 'function':
            print(f'   ❌ type should be function, got {tool[\"type\"]}')
        
        if not isinstance(tool['name'], str):
            print(f'   ❌ name should be string, got {type(tool[\"name\"])}')
        
        if tool['parameters'] is not None and not isinstance(tool['parameters'], dict):
            print(f'   ❌ parameters should be dict or null, got {type(tool[\"parameters\"])}')
        
        if not isinstance(tool['strict'], bool):
            print(f'   ❌ strict should be boolean, got {type(tool[\"strict\"])}')
    
    print()