from django.shortcuts import render, get_object_or_404
from .models import User, Account


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

    context = {
            'account': account,
            }
    return render(request, 'banking_system/account_details.html', context)

def create_customer_account(request):
    if request.method == "POST":
         user_id = request.user.id
         print(user_id)
         User.create_customer_account(customer_foreign_key=user_id)

    response = render(request, 'banking_system/index.html', {})
    response['HX-Redirect'] = request.META['HTTP_HX_CURRENT_URL']
    return response
