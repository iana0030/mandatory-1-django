from django.shortcuts import render, get_object_or_404
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
