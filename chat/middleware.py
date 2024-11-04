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
            response = HttpResponse()
            origin = request.headers.get('Origin')
            if origin:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Requested-With'
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Max-Age'] = '86400'
            return response
        
        if request.path.startswith('/chat/'):
            return None
            
        return super().process_view(request, callback, callback_args, callback_kwargs)

    def process_response(self, request, response):
        response = super().process_response(request, response)
        
        origin = request.headers.get('Origin')
        if origin:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Requested-With'
            response['Access-Control-Max-Age'] = '86400'
            response['Vary'] = 'Origin'
        
        logger.debug(f"Response headers: {dict(response.headers)}")
        return response 