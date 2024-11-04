import os
from waitress import serve
from citizens_llm_chat.wsgi import application

# Get port from environment variable with explicit casting to int
port = int(os.environ.get("PORT", 10000))  # Changed default to 10000 for Render

print(f"Starting server on port {port}")  # Add logging for debugging

# Explicitly bind to all interfaces (0.0.0.0) and the specified port
serve(application, host="0.0.0.0", port=port, url_scheme='https') 