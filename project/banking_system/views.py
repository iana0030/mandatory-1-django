from django.shortcuts import render
from .models import Ledger, Customer, Account, User
from decimal import *


def index(request):
    return render(request, 'banking_system/index.html', {})

# ledger view functions


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
        return render(request, 'banking_system/index.html')


def create_ledger_row(request):
    if request.method == "POST":
        account_id = request.POST["account_id"]
        amount = request.POST["amount"]
        text = request.POST["text"]
        account = Account.objects.get(pk=account_id)
        new_ledger_row = Ledger.create(account, amount, text)
        return render(request, 'banking_system/index.html', context={"new_ledger_row": new_ledger_row})


def ledger_list(request):
    if request.method == 'GET':
        ledger = Ledger.objects.all()
        return render(request, 'banking_system/ledger_list.html', {'ledger': ledger})
