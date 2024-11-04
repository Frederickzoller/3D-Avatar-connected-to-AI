from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, CustomAuthToken

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'conversations', ChatViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),
] 