from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user-accounts/', include('login_app.urls')),
    path('banking_system/', include('banking_system.urls')),
]
