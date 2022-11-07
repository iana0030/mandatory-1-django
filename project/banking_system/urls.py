from django.urls import path
from . import views

app_name = "banking_system"

urlpatterns = [
    # GET HTTP methods
    path('', views.index, name='index'),
    path('view_all_customers', views.view_all_customers , name='view_all_customers'),
    path('view_all_accounts', views.view_all_accounts , name='view_all_accounts'),

    # POST HTTP methods
    path('create_user', views.create_user, name='create_user'),
    path('create_customer', views.create_customer, name='create_customer'),
    path('create_customer_account', views.create_customer_account , name='create_customer_account'),

    # PATCH HTTP methods
    path('change_customer_rank', views.change_customer_rank , name='change_customer_rank'),
]
