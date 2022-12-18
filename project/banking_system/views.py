from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect #NEW
from django.urls import reverse #New

import pyotp
from decimal import *

from .models import Ledger, Customer, Account, User

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
    if request.method == "GET":
        user_id = request.user.id
        customer = Customer.objects.get(user=User.objects.get(pk=user_id))
        accounts = Account.objects.filter(customer=customer)

        for account in accounts:
            account.bal = account.balance
            print(account.bal)

        return render(request, 'banking_system/customer_bank.html', {'accounts': accounts})


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
        customers = Customer.view_all_customers()

        return render(request, 'banking_system/customers_list_partial.html', {'customers': customers})


@login_required
def view_all_accounts(request):
    if request.method == 'GET':
        accounts = Account.view_all_accounts()

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
        sender_account_number = request.POST["sender_account_number"]
        receiver_account_number = request.POST["receiver_account_number"]
        amount = Decimal(request.POST["amount"])
        text = request.POST["text"]

        sender_account = Account.objects.get(number=sender_account_number)
        receiver_account = Account.objects.get(number=receiver_account_number)

        Ledger.make_transactions(sender_account, receiver_account, amount, text)

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
# POST HTTP methods
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        new_user = User.create_user(username, password, email, first_name, last_name)
        response = render(request, 'banking_system/user_bank.html', {'new_user': new_user})
        response['HX-redirect'] = request.META['HTTP_HX_CURRENT_URL']
        return response


def create_customer(request):
    if request.method == 'GET':
        return render(request, 'banking_system/create_customer.html')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        rank = request.POST['rank']
        secret_otp = pyotp.random_base32()

        new_user = User.objects.create_user(username, first_name=first_name, last_name=last_name, email=email, password=password)
        # new_user = User.create_user(username, password, email, first_name, last_name)
        # new_customer = Customer.create_customer(username, password, first_name, last_name, address, phone_number, rank, new_user, secret_otp)
        new_customer = Customer.create_customer(username, password, first_name, last_name, address, phone_number, rank, new_user)

        response = render(request, 'banking_system/create_customer.html', {'new_customer': new_customer})
        response['HX-redirect'] = request.META['HTTP_HX_CURRENT_URL']
        return response


def create_customer_account(request):
    if request.method == 'POST':
        customer_foreign_key = request.POST['customer_primary_key']
        account_name = request.POST['customer_account_name']

        customer = get_object_or_404(Customer, pk=customer_foreign_key)

        new_customer_account = Account.create_customer_account(customer, account_name)

        response = render(request, 'banking_system/create_customer.html', {'new_customer_account': new_customer_account})
        response['HX-redirect'] = request.META['HTTP_HX_CURRENT_URL']
        return response

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

def transfer_money_to_other_bank(request):
    if request.method == 'POST':
        sender_account_number = request.POST['sender_account_number']
        receiver_account_number = request.POST['receiver_account_number']
        amount = request.POST['amount']
        text = request.POST['text']

        Account.transfer_money_to_other_bank(sender_account_number, receiver_account_number, amount, text)

        return render(request, 'banking_system/customer_bank.html')

# PATCH HTTP methods
def change_customer_rank(request):
    if request.method == 'GET':
        return render(request, 'banking_system/change_rank.html')

    if request.method == 'PATCH':
        customer_primary_key = request.PATCH['customer_primary_key']
        new_rank = request.PATCH['new_rank']

        updated_user = Customer.change_customer_rank(customer_primary_key, new_rank)
        response = render(request, 'banking_system/change_rank.html', {'updated_user': updated_user})
        response['HX-redirect'] = request.META['HTTP_HX_CURRENT_URL']
        return response
