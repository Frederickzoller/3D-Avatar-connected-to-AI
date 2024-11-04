from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ApiCSRFMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        logger.debug(f"Processing request: {request.method} {request.path}")
        logger.debug(f"Headers: {dict(request.headers)}")
        
        if request.method == 'OPTIONS':
            return HttpResponse()
        
        if (request.path.startswith('/chat/') or 
            request.path.endswith('/login') or 
            request.path.endswith('/login/')):
            return None
            
        return super().process_view(request, callback, callback_args, callback_kwargs)

    def process_response(self, request, response):
        response = super().process_response(request, response)
        
        origin = request.headers.get('Origin')
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response['Access-Control-Max-Age'] = '86400'
        
        logger.debug(f"Response headers: {dict(response.headers)}")
        return response 