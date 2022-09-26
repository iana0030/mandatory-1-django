from django.urls import path
from . import views

app_name = "banking_system"

urlpatterns = [
    path('', views.index, name='index'),
]
