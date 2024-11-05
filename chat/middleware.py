from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponse
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)

class ApiCSRFMiddleware(CsrfViewMiddleware):
    def _add_cors_headers(self, response, request):
        origin = request.headers.get('Origin', '')
        
        # More permissive CORS in development
        if settings.DEBUG:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
        # Strict CORS in production
        elif origin in settings.CORS_ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
        
        # Common headers for both environments
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = (
            'Origin, Content-Type, Accept, Authorization, X-Requested-With, '
            'X-CSRFToken, X-HTTP-Method-Override'
        )
        response['Access-Control-Max-Age'] = '86400'
        response['Vary'] = 'Origin'

        return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Skip CSRF for authentication endpoints
        if request.path.startswith('/chat/login/'):
            return None
            
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = HttpResponse(status=200)
            self._add_cors_headers(response, request)
            return response

        return super().process_view(request, callback, callback_args, callback_kwargs)

    def process_response(self, request, response):
        response = super().process_response(request, response)
        self._add_cors_headers(response, request)
        
        # Log failed requests in development
        if settings.DEBUG and response.status_code >= 400:
            logger.error(f"""
                Request failed:
                Path: {request.path}
                Method: {request.method}
                Status: {response.status_code}
                Headers: {dict(request.headers)}
                Body: {request.body.decode() if request.body else 'No body'}
            """)
            
        return response