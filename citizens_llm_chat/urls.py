from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chat.views import CustomAuthToken, ConversationViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'chat/conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('', include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 