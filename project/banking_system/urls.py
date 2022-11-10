from django.urls import path
from . import views

app_name = "banking_system"

urlpatterns = [
    path('', views.index, name='index'),
    path('account_details/<int:pk>/', views.view_account_details, name='account_details'),

    path('create_account/', views.create_account, name="create_account"),
]
