import os
import json
import asyncio
from openai import AsyncOpenAI

async def test_responses_api():
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Simple test tool
    test_tool = {
        'type': 'function',
        'name': 'test_function',
        'description': 'A test function',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'A test parameter'
                }
            },
            'required': ['query'],
            'additionalProperties': False
        },
        'strict': True
    }
    
    try:
        print('Testing Responses API...')
        response = await client.responses.create(
            model='gpt-4.1-mini',
            input='Please call the test function with query hello',
            tools=[test_tool],
            tool_choice='required'
        )
        print('✅ Success!')
        print(response)
    except Exception as e:
        print(f'❌ Error: {e}')
        print(f'Type: {type(e)}')

asyncio.run(test_responses_api())