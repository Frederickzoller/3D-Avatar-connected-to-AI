from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

class ApiCSRFMiddleware(CsrfViewMiddleware):
    def _add_cors_headers(self, response, request):
        origin = request.headers.get('Origin', '')
        
        # Check if origin is in allowed origins
        if origin in settings.CORS_ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            
            # Log successful CORS handling
            logger.debug(f"CORS headers added for origin: {origin}")
        else:
            logger.warning(f"Origin not allowed: {origin}")
            
        return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Skip CSRF check for login endpoint
        if request.path.startswith('/chat/login/'):
            return None
            
        # Handle OPTIONS requests
        if request.method == 'OPTIONS':
            response = self._add_cors_headers(HttpResponse(), request)
            return response
            
        return super().process_view(request, callback, callback_args, callback_kwargs)

    def process_response(self, request, response):
        response = super().process_response(request, response)
        return self._add_cors_headers(response, request)