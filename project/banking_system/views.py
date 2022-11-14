from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from .models import User, Customer, Account, Ledger


def index(request):
    # VIEWING ACCOUNTS
    if request.method == "GET":
        user_id = request.user.id
        accounts = Account.objects.filter(customer_fk_id=user_id)

        context = {
                'accounts': accounts
                }

        return render(request, 'banking_system/index.html', context)

def view_account_details(request, pk):
    account = get_object_or_404(Account, pk=pk)
    customer_movements = Customer.get_customer_movements(foreign_key=pk)
    account_movements = Ledger.objects.filter(account_id=account.account_id)

    context = {
            'account': account,
            'customer_movements': customer_movements,
            'account_movements': account_movements,
            }

    return render(request, 'banking_system/account_details.html', context)


# Might be redundant, it also doesn't work because it needs the fk_id to be a Customer instance
def create_account(request):
    if request.method == "POST":
         user_id = request.user.id
         # accounts = Account.objects.filter(customer_fk_id=user_id)
         account = get_object_or_404(Account, pk=user_id)
         print(account.customer_fk_id.id)
         customer_fk_id = account.customer_fk_id
         account_name = request.POST['account_name']
         # User.create_customer_account(customer_foreign_key=user_id)
         Account.create(account_name, customer_fk_id)

    response = render(request, 'banking_system/index.html', {})
    response['HX-Redirect'] = request.META['HTTP_HX_CURRENT_URL']
    return response

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
