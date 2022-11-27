from django.urls import path
from . import views

app_name = "banking_system"

urlpatterns = [
    # GET HTTP methods
    path('', views.index, name='index'),
    path('ledger_list/', views.ledger_list, name='ledger_list'),
    path('account_details/<int:pk>/', views.view_account_details, name='account_details'),
    path('view_all_customers', views.view_all_customers , name='view_all_customers'),
    path('view_all_accounts', views.view_all_accounts , name='view_all_accounts'),
    path('get_customer_movements/<int:pk>/', views.get_customer_movements, name='get_customer_movements'),

    # POST HTTP methods
    path('create_user', views.create_user, name='create_user'),
    path('create_customer', views.create_customer, name='create_customer'),
    path('create_customer_account', views.create_customer_account , name='create_customer_account'),
    path('create_account/', views.create_account, name="create_account"),
    path('make_transactions/', views.make_transactions, name='make_transactions'),
    path('create_ledger_row/', views.create_ledger_row, name='create_ledger_row'),
    path('take_loan/', views.take_loan, name='take_loan'),
    path('pay_loan/', views.pay_loan, name='pay_loan'),

    # Special POST HTTP methods
    path('receive_money_from_other_bank/', views.receive_money_from_other_bank, name="receive_money_from_other_bank"),

    # PATCH HTTP methods
    path('change_customer_rank', views.change_customer_rank , name='change_customer_rank'),
]
