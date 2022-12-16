from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from .models import Ledger, Customer, Account, User
from decimal import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect #NEW
from django.urls import reverse #New



# REST-FRAMEWORK
from rest_framework import status
from .serializers import LedgerSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view

# API
@api_view(['GET'])
def get_balancesheet(request, account_id, *args, **kwargs):
    try:
        if request.method == 'GET':
            ledger = Ledger.objects.filter(account_id=account_id)
            serializer = LedgerSerializer(ledger, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Ledger.DoesNotExist:
        return Response({'status': 'failed'}, status=status.HTTP_404_NOT_FOUND)
        
# GET HTTP methods
@login_required
def index(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('banking_system:user_bank'))
    else:
        return HttpResponseRedirect(reverse('banking_system:customer_bank'))
    

    # VIEWING ACCOUNTS
    if request.method == "GET":
        user_id = request.user.id
        accounts = Account.objects.filter(customer_id=user_id)

        context = {
            'accounts': accounts
        }

    return render(request, 'banking_system/index.html', context)


# cutomer_page
def customer_index(request):
    return render(request, 'banking_system/customer_bank.html', {})


# user_page
def user_index(request):
    return render(request, 'banking_system/user_bank.html', {})



@login_required
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
    

@login_required
def ledger_list(request):
    if request.method == 'GET':
        ledger = Ledger.objects.all()
        return render(request, 'banking_system/ledger_list.html', {'ledger': ledger})


@login_required
def view_all_customers(request):
    if request.method == 'GET':
        customers = User.view_all_customers()

        return render(request, 'banking_system/customers_list_partial.html', {'customers': customers})


@login_required
def view_all_accounts(request):
    if request.method == 'GET':
        accounts = User.view_all_accounts()

        return render(request, 'banking_system/accounts_list_partial.html', {'accounts': accounts})


@login_required
def get_customer_movements(request, pk):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, pk=pk)
        customer_movements = customer.get_customer_movements()

        return render(request, 'banking_system/customer_movements_partial.html',
            {
                'customer_accounts': customer_movements['customer_accounts'],
                'customer_account_movements': customer_movements['customer_account_movements']
            }
        )


# POST HTTP methods
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

        response = render(request, 'banking_system/loan_account.html', {})
        response['HX-Redirect'] = request.META['HTTP_HX_CURRENT_URL']
        return response

    return render(request, 'banking_system/loan_account.html', {})



def make_transactions(request):
    if request.method == 'POST':
        sender_account_id = request.POST["sender_account_id"]
        receiver_account_id = request.POST["receiver_account_id"]
        amount = Decimal(request.POST["amount"])
        text = request.POST["text"]
        sender_account = Account.objects.get(account_id=sender_account_id)
        print(sender_account)
        receiver_account = Account.objects.get(account_id=receiver_account_id)
        Ledger.make_transactions(
            sender_account, receiver_account, amount, text)
    return render(request, 'banking_system/make_transactions.html')


def create_ledger_row(request):
    new_ledger_row = []
    if request.method == "POST":
        account_id = request.POST["account_id"]
        amount = request.POST["amount"]
        text = request.POST["text"]
        account = Account.objects.get(pk=account_id)
        new_ledger_row = Ledger.create(account, amount, text)
    return render(request, 'banking_system/make_transactions.html', context={"new_ledger_row": new_ledger_row})


def ledger_list(request):
    if request.method == 'GET':
        ledger = Ledger.objects.all()
    return render(request, 'banking_system/ledger_list.html', {'ledger': ledger})
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
    return render(request, 'banking_system/user_bank.html', {'new_user': new_user})


def create_customer(request):
    new_customer = []
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        rank = request.POST['rank']
        user_primary_key = request.POST['user_primary_key']
        secret_otp = pyotp.random_base32()

        user = get_object_or_404(User, pk=user_primary_key)
        new_customer = User.create_customer(username, password, first_name, last_name, address, phone_number, rank, user, secret_otp)

    return render(request, 'banking_system/create_customer.html', {'new_customer': new_customer})


def create_customer_account(request):
    if request.method == 'POST':
        customer_foreign_key = request.POST['customer_foreign_key']

        new_customer_account = User.create_customer_account(
            customer_foreign_key)

    return render(request, 'banking_system/create_customer.html', {'new_customer_account': new_customer_account})


def take_loan(request):
    if request.method == 'POST':
        deposit_account_primary_key = request.POST['deposit_account_primary_key']
        amount = Decimal(request.POST['amount'])
        text = request.POST['text']
        customer = Customer.objects.get(pk=1)

        loan_account = customer.take_loan(deposit_account_primary_key, amount, text)

        return render(request, 'banking_system/index.html', {'loan_account':loan_account})


def pay_loan(request):
    if request.method == 'POST':
        account_primary_key = request.POST.get('account_primary_key')
        amount = Decimal(request.POST.get('amount'))
        text = request.POST.get('text')
        customer = Customer.objects.get(pk=1)

        customer.pay_loan(account_primary_key, amount, text)

        return render(request, 'banking_system/pay_loan')


# PATCH HTTP methods
def change_customer_rank(request):
    updated_user = []
    if request.method == 'PATCH':
        customer_primary_key = request.PATCH['customer_primary_key']
        new_rank = request.PATCH['new_rank']
        updated_user = User.change_customer_rank(
            customer_primary_key, new_rank)
    return render(request, 'banking_system/change_rank.html', {'updated_user': updated_user})