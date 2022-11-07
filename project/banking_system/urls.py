from django.urls import path
from . import views

app_name = "banking_system"

urlpatterns = [
    path('', views.index, name='index'),
    path('create_user', views.create_user, name='create_user'),
    path('create_customer', views.create_customer, name='create_customer'),
]
