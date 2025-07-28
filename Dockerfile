FROM ghcr.io/open-webui/open-webui:main

RUN pip install --upgrade pip --upgrade google-auth-oauthlib --upgrade google-api-python-client --upgrade google-auth-httplib2 openai openai-agents pydantic

# Copy the OAuth deployment script
COPY deploy_oauth_callback.sh /app/deploy_oauth_callback.sh
RUN chmod +x /app/deploy_oauth_callback.sh

# Create a startup script that deploys OAuth callback and starts Open WebUI
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Use our custom startup script
CMD ["/app/startup.sh"]

