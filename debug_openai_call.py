#!/usr/bin/env python3
"""
Debug the OpenAI API call from the Google Workspace Pipe
"""

import requests


def test_openai_api_call():
    """Test the exact same API call that the pipe would make"""

    # Simulate what the pipe does
    api_key = "sk-proj-..."  # This is the placeholder from the pipe

    payload = {
        "model": "gpt-4.1",
        "input": "user: Please find the Green New Deal document on my Google Drive.",
        "tools": [
            {
                "type": "function",
                "name": "list_drive_files",
                "description": "List files in Google Drive. Shows up to 50 files by default.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to filter files (optional). Example: 'name contains \"report\"' or 'mimeType=\"application/pdf\"'",
                        }
                    },
                },
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print("Testing OpenAI Responses API call...")
    print("=" * 60)
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    print(f"Model: {payload['model']}")
    print(f"Input: {payload['input']}")
    print(f"Number of tools: {len(payload['tools'])}")
    print()

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers=headers,
            json=payload,
            timeout=10,
        )

        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")


def test_with_chat_completions():
    """Test with Chat Completions API for comparison"""

    api_key = "sk-proj-..."

    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "user",
                "content": "Please find the Green New Deal document on my Google Drive.",
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print("\nTesting Chat Completions API for comparison...")
    print("=" * 60)

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10,
        )

        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    test_openai_api_call()
    test_with_chat_completions()
