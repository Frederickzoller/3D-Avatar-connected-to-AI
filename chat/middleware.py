from django.middleware.csrf import CsrfViewMiddleware

class ApiCSRFMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if (request.path.startswith('/chat/') or 
            request.path.endswith('/login') or 
            request.path.endswith('/login/')):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs) 