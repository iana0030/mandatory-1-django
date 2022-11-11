from django.urls import path
from . import views

app_name = "banking_system"

urlpatterns = [
    path('', views.index, name='index'),
    path('make_transactions/', views.make_transactions, name='make_transactions'),
    path('create_ledger_row/', views.create_ledger_row, name='create_ledger_row'),
    path('ledger_list/', views.ledger_list, name='ledger_list'),
]
