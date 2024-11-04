from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ApiCSRFMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.method == "OPTIONS":
            return self._handle_preflight(request)

        if request.path.startswith('/chat/'):
            return None

        return super().process_view(request, callback, callback_args, callback_kwargs)

    def _handle_preflight(self, request):
        response = HttpResponse(status=200)
        self._add_cors_headers(response, request)
        return response

    def process_response(self, request, response):
        response = super().process_response(request, response)
        if request.path.startswith('/chat/'):
            self._add_cors_headers(response, request)
        return response

    def _add_cors_headers(self, response, request):
        origin = request.headers.get('Origin', '')
        
        if origin in settings.CORS_ALLOWED_ORIGINS or settings.DEBUG:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Requested-With'
            response['Access-Control-Max-Age'] = '86400'
            response['Vary'] = 'Origin'

        return response