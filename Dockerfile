FROM ghcr.io/open-webui/open-webui:main

RUN pip install --upgrade pip google-auth-oauthlib google-api-python-client google-auth-httplib2 openai openai-agents pydantic

# ...existing code...
