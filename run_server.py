import os
from waitress import serve
from citizens_llm_chat.wsgi import application
import logging
import socket

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('waitress')

def get_available_port():
    """Get an available port, with better error handling for Render environment"""
    try:
        # First try the PORT from environment
        port = int(os.environ.get("PORT", 10000))
        logger.info(f"Attempting to use port {port}")
        
        # Test if we can bind to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.close()
        return port
    except (ValueError, socket.error) as e:
        logger.warning(f"Could not use specified port: {e}")
        
        # If we're on Render, we should use their PORT
        if os.environ.get('RENDER'):
            logger.error("Failed to bind to Render's PORT")
            raise
            
        # For local development, find an available port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 0))
        port = sock.getsockname()[1]
        sock.close()
        logger.info(f"Using alternative port {port}")
        return port

def main():
    try:
        # Load environment variables early
        from dotenv import load_dotenv
        load_dotenv()
        
        port = get_available_port()
        
        # Configure Waitress with production-ready settings
        server_options = {
            'host': '0.0.0.0',
            'port': port,
            'url_scheme': 'https',
            'threads': int(os.environ.get('WAITRESS_THREADS', '4')),
            'channel_timeout': 300,
            'connection_limit': 1000,
            'cleanup_interval': 30,
            'max_request_header_size': 16384,
            'max_request_body_size': 1073741824,
            'asyncore_use_poll': True,
            'outbuf_overflow': 1048576,
            'inbuf_overflow': 524288,
            'clear_untrusted_proxy_headers': True,
            'trusted_proxy_headers': {'x-forwarded-proto'},
            'trusted_proxy': None,
            'log_untrusted_proxy_headers': True,
        }

        # Log all environment variables (excluding sensitive ones)
        logger.info("Environment variables:")
        for key in os.environ:
            if not any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password']):
                logger.info(f"{key}: {os.environ[key]}")

        # Start server with better error handling
        logger.info(f"Starting server on http://0.0.0.0:{port}")
        serve(application, **server_options)
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()