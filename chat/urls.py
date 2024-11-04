from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .views import ChatViewSet, CustomAuthToken

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'conversations', ChatViewSet, basename='conversation')

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'message': 'Welcome to the Citizens LLM Chat API',
        'endpoints': {
            'login': '/chat/login/',
            'conversations': '/chat/conversations/',
        },
        'documentation': 'Please login to access the API endpoints'
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),
] 