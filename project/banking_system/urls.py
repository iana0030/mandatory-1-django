from django.urls import path
from . import views

app_name = "banking_system"

urlpatterns = [
    # GET HTTP methods
    path('', views.index, name='index'),
    path('ledger_list/', views.ledger_list, name='ledger_list'),
    path('account_details/<int:pk>/', views.view_account_details, name='account_details'),
    path('view_all_customers', views.view_all_customers, name='view_all_customers'),
    path('view_all_accounts', views.view_all_accounts, name='view_all_accounts'),

    # POST HTTP methods
    path('create_user', views.create_user, name='create_user'),
    path('create_customer', views.create_customer, name='create_customer'),
    path('create_customer_account', views.create_customer_account, name='create_customer_account'),
    path('create_account/', views.create_account, name="create_account"),
    path('make_transactions/', views.make_transactions, name='make_transactions'),
    path('create_ledger_row/', views.create_ledger_row, name='create_ledger_row'),
    path('take_loan', views.take_loan, name='take_loan'),
    path('pay_loan/', views.pay_loan, name='pay_loan'),
    path('transfer_money_to_other_bank', views.transfer_money_to_other_bank, name="transfer_money_to_other_bank"),
    
    # Customer and user sepereated
    path('user_bank/', views.user_index, name='user_bank'),
    path('customer_bank/', views.customer_index, name='customer_bank'),

    # PATCH HTTP methods
    path('change_customer_rank', views.change_customer_rank , name='change_customer_rank'),
    
    # API 
    path('api/get_balancesheet/<int:account_id>/', views.get_balancesheet, name='get_balancesheet'),
    path('statement/<int:account_id>/', views.statement, name='statement')
]
