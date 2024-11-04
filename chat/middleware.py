from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponse

class ApiCSRFMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.method == 'OPTIONS':
            return HttpResponse()
        if (request.path.startswith('/chat/') or 
            request.path.endswith('/login') or 
            request.path.endswith('/login/')):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)

    def process_response(self, request, response):
        response = super().process_response(request, response)
        
        # Always add CORS headers
        origin = request.headers.get('Origin', '*')
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT, DELETE'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        return response 