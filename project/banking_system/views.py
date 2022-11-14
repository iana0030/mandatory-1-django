from django.shortcuts import render
from .models import User, Customer, Account, Ledger


def index(request):
    return render(request, 'banking_system/index.html', {})

# USER methods
# GET HTTP methods
def view_all_customers(request):
    if request.method == 'GET':
        customers = User.view_all_customers()
        
        return render(request, 'banking_system/customers_list_partial.html', {'customers': customers})

def view_all_accounts(request):
    if request.method == 'GET':
        accounts = User.view_all_accounts()
        
        return render(request, 'banking_system/accounts_list_partial.html', {'accounts': accounts})

# POST HTTP methods
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        new_user = User.create_user(username, email, first_name, last_name)
        
        return render(request, 'banking_system/index.html', {'new_user': new_user})

def create_customer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        rank = request.POST['rank']
        user_foreign_key = request.POST['user_foreign_key']

        new_customer = User.create_customer(username, password, first_name, last_name, address, phone_number, rank, user_foreign_key)
        
        return render(request, 'banking_system/index.html', {'new_customer': new_customer})

def create_customer_account(request):
    if request.method == 'POST':
        customer_foreign_key = request.POST['customer_foreign_key']

        new_customer_account = User.create_customer_account(customer_foreign_key)

        return render(request, 'banking_system/index.html', {'new_customer_account': new_customer_account})

# PATCH HTTP methods
def change_customer_rank(request):
    if request.method == 'PATCH':
        customer_primary_key = request.PATCH['customer_primary_key']
        new_rank = request.PATCH['new_rank']
        updated_user = User.change_customer_rank(customer_primary_key, new_rank)

        return render(request, 'banking_system/index.html', {'updated_user': updated_user})