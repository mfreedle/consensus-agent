#!/usr/bin/env python3
"""
Simple HTTP server to serve OAuth success page.
This runs alongside Open WebUI to handle OAuth callbacks.
"""

import http.server
import socketserver
import urllib.parse
import os
import threading

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for OAuth callback."""
        if self.path.startswith('/oauth-success'):
            # Serve the success page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read the success page HTML
            html_path = '/app/backend/data/opt/oauth-success.html'
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                self.wfile.write(html_content.encode('utf-8'))
            except FileNotFoundError:
                self.wfile.write(b'''
                <html><body>
                <h1>OAuth Success!</h1>
                <p>Authorization completed successfully!</p>
                <p>Please copy the authorization code from the URL and return to Open WebUI.</p>
                <p>You may close this tab and go outside and play! 🌟</p>
                </body></html>
                ''')
        else:
            # For any other path, show a simple message
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
            <html><body>
            <h1>OAuth Callback Server</h1>
            <p>This server handles Google OAuth callbacks for Open WebUI.</p>
            </body></html>
            ''')

def start_oauth_server(port=8090):
    """Start the OAuth callback server."""
    try:
        with socketserver.TCPServer(("", port), OAuthCallbackHandler) as httpd:
            print(f"✅ OAuth callback server started on http://localhost:{port}")
            print(f"🔗 OAuth success page: http://localhost:{port}/oauth-success")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Failed to start OAuth server on port {port}: {e}")

def start_oauth_server_background(port=8090):
    """Start the OAuth server in a background thread."""
    server_thread = threading.Thread(target=start_oauth_server, args=(port,), daemon=True)
    server_thread.start()
    return server_thread

if __name__ == "__main__":
    start_oauth_server(8090)
