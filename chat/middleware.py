from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ApiCSRFMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Skip logging for health check requests
        if not request.path.startswith('/health/'):
            logger.debug(f"Processing request: {request.method} {request.path}")
            logger.debug(f"Headers: {dict(request.headers)}")
        
        # Handle OPTIONS requests
        if request.method == 'OPTIONS':
            response = HttpResponse()
            self._add_cors_headers(response, request)
            return response
        
        # Skip CSRF for API endpoints
        if request.path.startswith('/chat/') or request.path == '/':
            return None
            
        return super().process_view(request, callback, callback_args, callback_kwargs)

    def process_response(self, request, response):
        response = super().process_response(request, response)
        
        # Add CORS headers
        self._add_cors_headers(response, request)
        
        # Skip logging for health check requests
        if not request.path.startswith('/health/'):
            logger.debug(f"Response headers: {dict(response.headers)}")
        
        return response

    def _add_cors_headers(self, response, request):
        origin = request.headers.get('Origin', '')
        
        allowed_origins = [
            'http://localhost:5500',
            'http://127.0.0.1:5500',
            'https://threed-avatar-connected-to-ai-1.onrender.com'
        ]
        
        if origin in allowed_origins or settings.DEBUG:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Requested-With'
            response['Access-Control-Max-Age'] = '86400'
            response['Vary'] = 'Origin'