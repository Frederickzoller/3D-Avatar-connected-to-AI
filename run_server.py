import os
from waitress import serve
from citizens_llm_chat.wsgi import application
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('waitress')

# Get port from environment variable with better error handling
try:
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Using port {port}")
except ValueError as e:
    logger.error(f"Invalid PORT value: {os.environ.get('PORT')}")
    port = 10000

# Test if port is available
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(('0.0.0.0', port))
    sock.close()
    logger.info(f"Port {port} is available")
except socket.error as e:
    logger.error(f"Port {port} is not available: {e}")
    # Try to find an available port
    sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 0))
    port = sock.getsockname()[1]
    sock.close()
    logger.info(f"Using alternative port {port}")

# Configure Waitress server options
server_options = {
    'host': '0.0.0.0',
    'port': port,
    'url_scheme': 'https',
    'threads': 4,
    'channel_timeout': 30,
    'connection_limit': 100,
    'cleanup_interval': 30,
    'max_request_header_size': 16384,
    'max_request_body_size': 1073741824,
    'asyncore_use_poll': True,
    'outbuf_overflow': 1048576,
    'inbuf_overflow': 524288,
    'clear_untrusted_proxy_headers': True,  # Add this for security
    'trusted_proxy_headers': {'x-forwarded-proto'},  # Trust only specific headers
    'trusted_proxy': None,  # Don't trust any proxy by default
}

# Log all server options for debugging
logger.info("Server options:")
for key, value in server_options.items():
    logger.info(f"{key}: {value}")

try:
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    serve(application, **server_options)
except Exception as e:
    logger.error(f"Failed to start server: {e}")
    raise 