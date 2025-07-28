FROM ghcr.io/open-webui/open-webui:main

RUN pip install --upgrade pip --upgrade google-auth-oauthlib --upgrade google-api-python-client --upgrade google-auth-httplib2 openai openai-agents pydantic

