from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from chat.views import CustomAuthToken

urlpatterns = [
    path('', RedirectView.as_view(url='/chat/', permanent=True)),  # Redirect root to /chat/
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
] 