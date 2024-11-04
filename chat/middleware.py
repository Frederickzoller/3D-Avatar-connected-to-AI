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
        if request.method == 'OPTIONS':
            response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Access-Control-Max-Age'] = '86400'  # 24 hours
        return response 