from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.http import HttpResponse
from chat.views import CustomAuthToken

def health_check(request):
    """Simple health check endpoint for monitoring"""
    return HttpResponse(status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('api-token-auth/', CustomAuthToken.as_view()),
    # Add health check endpoint
    path('health/', health_check, name='health_check'),
    # Redirect root to chat only for GET requests
    path('', lambda request: (
        RedirectView.as_view(url='/chat/')(request) 
        if request.method == 'GET' 
        else HttpResponse(status=200)
    )),
] 