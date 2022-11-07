from django.urls import path
from . import views

app_name = "banking_system"

urlpatterns = [
    path('', views.index, name='index'),
    path('create_user', views.create_user, name='create_user'),
    path('create_customer', views.create_customer, name='create_customer'),
    path('view_all_customers', views.view_all_customers , name='view_all_customers'),
    path('view_all_accounts', views.view_all_accounts , name='view_all_accounts'),
]
