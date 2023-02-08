from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum

import random
import requests
from decimal import *


# represents the User class which is used by bank employees for administration or by regular customers
def __str__(self):
    return f"ID: {self.id} | USERNAME: {self.username} | EMAIL: {self.email} | FIRST NAME: {self.first_name} | LAST NAME: {self.last_name}"


# creates the user
# User.create("username", "email", "first_name", "last_name")
@classmethod
def create_user(cls, username, password, email, first_name, last_name):
    user = cls.objects.create(
        username = username,
        email = email,
        password = password,
        first_name = first_name,
        last_name = last_name
    )
    return user

# Add defined methods to the User
User.add_to_class("__str__", __str__)
User.add_to_class("create_user", create_user)


# represents the Customer class
class Customer(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    rank = models.CharField(max_length=6)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"ID {self.id} | USERNAME: {self.username} | PASSWORD: {self.password} | FIRST NAME {self.first_name} | LAST NAME: {self.last_name} | ADDRESS: {self.address} | PHONE NUMBER: {self.phone_number} | RANK: {self.rank} | USER_ID: {self.user.id}"

    # User.view_all_customers()
    @classmethod
    def view_all_customers(cls):
        all_customers = cls.objects.all()
        return all_customers


    # User.create_customer("username", "password", "first_name", "last_name", "address", "phone_number", "rank", user_primary_key)
    @classmethod
    def create_customer(cls, username, password, first_name, last_name, address, phone_number, rank, user):
        # search for user
        customer = cls.objects.create(
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
            address = address,
            phone_number = phone_number,
            rank = rank,
            user = user,
        )
        return customer

    # User.change_customer_rank(customer_primary_key, "new_rank")
    @classmethod
    def change_customer_rank(cls, customer_primary_key, new_rank):
        customer = cls.objects.get(pk=customer_primary_key)
        customer.rank = new_rank
        customer.save()
        return cls.objects.get(pk=customer_primary_key)

    # retrieves all customer's accounts and accounts' movements
    # Customer.objects.get(pk=ID).get_customer_balance()
    # or assign Customer.objects.get(pk=ID) to variable like "customer"
    # customer.get_customer_movement()
    def get_customer_movements(self):
        # get all customer accounts
        customer_accounts = Account.objects.filter(customer_id=self.id)
        # get transactions those accounts made
        customer_account_movements = list()
        for customer_account in customer_accounts:
            # for each Account Customer owns get Ledger rows (transactions)
            customer_movements_queryset = Ledger.objects.filter(account_id=customer_account.id)

            # put each Ledger row (transaction) in list
            for customer_account_movement in customer_movements_queryset:
                customer_account_movements.append(customer_account_movement)

        records = {
            'customer_accounts': customer_accounts,
            'customer_account_movements': customer_account_movements
        }
        return records


    # creates the loan account for the customer
    # Customer.objects.get(pk=ID).take_loan(ACCOUNT_ID, 100, "Money")
    # or assign Customer.objects.get(pk=ID) to variable like "customer"
    # customer.take_loan(ACCOUNT_ID, 100, "Money")
    def take_loan(self, deposit_account_primary_key, amount, text):
        # get customer accounts
        available_accounts = self.get_customer_movements()["customer_accounts"]

        # check for customer rank and if the customer has available accounts for deposit
        if self.rank == 'basic':
            return "Can't make a loan. User is not of silver or gold rank."
        elif available_accounts.count() == 0:
            return "Customer doesn't have any accounts to deposit money from loan to."
        elif not available_accounts.get(id=deposit_account_primary_key):
            return "There is no account with such primary key that belongs to this customer."
        else:
            # find deposit account, create loan/withdrawal account, get loan account after ID is set by Django
            # then transfer money from one to another in case of error, transaction will ensure ACID
            deposit_account = Account.objects.get(pk=deposit_account_primary_key)
            with transaction.atomic():
                loan_account_account_number = Account.create_loan_account(self).number
                loan_account = Account.objects.get(number=loan_account_account_number)
                Ledger.make_transactions(loan_account, deposit_account, amount, text)


    # pays loan to loan account/s
    # since one customer can take multiple loans, he can pay of one loan partly,
    # one loan entirely and one loan partly or more loans entirely and one loan partly
    # Customer.objects.get(pk=ID).pay_loan(ACCOUNT_ID, 100, "Money")
    # or assign Customer.objects.get(pk=ID) to variable like "customer"
    # customer.pay_loan(ACCOUNT_ID, 100, "Money")
    def pay_loan(self, account_primary_key, amount, text):
        # check if the user has loans
        loan_accounts = Account.objects.all().filter(customer_id=self.id).filter(is_loan=True)

        # print("\n\n")
        # print(loan_accounts)
        # print("\n\n")
        if not len(loan_accounts):
            return "Customer doesn't have any loans."

        # get customer's account from where money will be transfered
        customer_account = Account.objects.get(pk=account_primary_key)

        # transform float or integer to Decimal
        amount = Decimal(amount)

        # validation
        if amount <= Decimal(0.00):
            return "Amount paid can't be 0.00. Please pay more money."
        elif amount > customer_account.balance:
            return "Can't transfer that much money. Insufficient funds."

        # pay loan on loan accounts
        for loan_account in loan_accounts:
            # balance on loan accounts will always be negative
            if -amount > loan_account.balance:
                # total takes snapshot of current loan account balance
                total = loan_account.balance

                # make transaction from user account to loan account
                Ledger.make_transactions(customer_account, loan_account, amount, text)

                return f"Paid {amount} of {total} on {loan_account.number} account. Need to pay {loan_account.balance} more."
            else:
                # make transaction from user account to loan account fully
                # if customer wanted to pay loan of 1000 and he is paying loan of 500, then 1000 += -500
                amount += loan_account.balance
                Ledger.make_transactions(customer_account, loan_account, -loan_account.balance, text)
                loan_account.delete()
        return

# represents Account class which can belong to one Customer
class Account(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    number = models.CharField(max_length=30)
    is_loan = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


    def __str__(self):
        return f"ID: {self.id} | NAME: {self.name} | NUMBER: {self.number} | IS LOAN: {self.is_loan} | CUSTOMER: {self.customer}"


    # creates new Account in Account table
    # Account.create("Main", "12131", False, CUSTOMER ID)
    @classmethod
    def create(cls, name, number, is_loan, customer):
        new_account = cls.objects.create(
            name     = name,
            number   = number,
            is_loan  = is_loan,
            customer = customer
        )
        return new_account


    # User.view_all_accounts()
    @classmethod
    def view_all_accounts(cls):
        all_accounts = cls.objects.all()
        return all_accounts


    # goes through Ledger table, gets all acounts with particular ID and then aggregates their amount into SUM
    # Account.objects.get(pk=ID).balance
    # or you can assign Account to variable like "account"
    # and then do account.balance
    @property
    def balance(self):
        return Decimal(Ledger.objects.filter(account_id=self.id).aggregate(Sum('amount'))['amount__sum'] or 0.00).quantize(Decimal('.00'))

    # Account.create_customer_account(customer, "account_name")
    @classmethod
    def create_customer_account(cls, customer, account_name):
        random_account_number = random.getrandbits(64)
        new_customer_account = cls.create(account_name, random_account_number, False, customer)
        return new_customer_account

    # creates loan account and connects it to the customer
    @classmethod
    def create_loan_account(cls, customer):
        random_account_number = random.getrandbits(64)
        new_loan_account = cls.create(f"LOAN{random_account_number}", random_account_number, True, customer)
        return new_loan_account

    # uses requests python library to send HTTP request to hit endpoint
    # on other running bank instance to simulatemoney transaction between two banks
    # other instance can be ran with command $python manage.py runserver 9000
    # as first instance/main project will be running on 8000
    @classmethod
    def transfer_money_to_other_bank(cls, sender_account_number, receiver_account_number, amount, text):
        amount = Decimal(amount)
        # check if the account exists and if it has more funds than it is being sent
        if not cls.objects.filter(number=sender_account_number).exists():
            return f'account with {sender_account_number} does not exist'
        if cls.objects.get(number=sender_account_number).balance < amount:
            return 'accounts does not have enough funds'

        # Create idempotent key
        key = f'{sender_account_number}{receiver_account_number}{amount}'
        idempotent_key = hash(key)

        # create payload with necessarry data for money transfer
        payload = {
            'receiver_account_number': receiver_account_number,

            'amount': amount,
            'text': text,
            'idempotent_key': idempotent_key,
        }
        # send request and receive response
        response = requests.post(settings.SECOND_BANK_URL, data=payload)
        if response.status_code == 201:
            sender_account = cls.objects.get(number=sender_account_number)
            Ledger.create(sender_account, -amount, text)
        else:
            print("Transaction already processed")

# represents the Ledger class which stores transactions in a way that bulk_create() creates two rows
# one row is deduction from one account, other row is addition to other account
class Ledger(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    time_stamp = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=200)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


    def __str__(self):
        return f"ID: {self.transaction_id} | ACCOUNT: {self.account} | AMOUNT: {self.amount} | CREATED_AT: {self.time_stamp} | TEXT: {self.text}"


    @classmethod
    def create(cls, account, amount, text):
        new_ledger_row = cls.objects.create(
            account     = account,
            amount      = amount,
            text        = text
        )
        return new_ledger_row


    # uses transaction and create to insert two rows in Ledger table
    # first row is sender account sending money, therefore amount being negative
    # second row is receiver account receiving money, therefore amount being positive
    # sender_account = Account.objects.get(pk=ID)
    # receiver_account = Account.objects.get(pk=ID)
    # Ledger.make_transactions(sender_account, receiver_account, 100, "Money")
    @classmethod
    def make_transactions(cls, sender_account, receiver_account, amount, text):
        with transaction.atomic():
            if sender_account.balance >= Decimal(amount) or sender_account.is_loan == True:
                cls.create(sender_account, -Decimal(amount), text)
                cls.create(receiver_account, Decimal(amount), text)
            else:
                print('Transaction not allowed. Balance too low!')
