from decimal import *
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum
import random

# after every defined method, that method with the same name is added to Django's User class via User.add_to_class method

# represents the User class which is used by bank employees for administration or by regular customers
def __str__(self):
    return f"{self.id} - {self.username} - {self.email} - {self.first_name} - {self.last_name}"

User.add_to_class("__str__", __str__)

# create the user
def create_user(username, email, first_name, last_name):
    user = User.objects.create(
        username = username,
        email = email,
        first_name = first_name,
        last_name = last_name
    )
    return user

User.add_to_class("create_user", create_user)

# create the customer for user
def create_customer(username, password, first_name, last_name, address, phone_number, rank, user_foreign_key):
    # search for user
    owner_user = User.objects.get(pk=user_foreign_key)
    if owner_user:
        customer = Customer.objects.create(
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
            address = address,
            phone_number = phone_number,
            rank = rank,
            user = owner_user
        )
        return customer
    return "User couldn't be found."

User.add_to_class("create_customer", create_customer)

def view_all_customers():
    all_customers = Customer.objects.all()
    return all_customers

User.add_to_class("view_all_customers", view_all_customers)

def view_all_accounts():
    all_accounts = Account.objects.all()
    return all_accounts

User.add_to_class("view_all_accounts", view_all_accounts)

def change_customer_rank(customer_primary_key, new_rank):
    customer = Customer.objects.get(pk=customer_primary_key)
    customer.rank = new_rank
    customer.save()
    return customer

User.add_to_class("change_customer_rank", change_customer_rank)

def create_customer_account(customer_foreign_key):
    random_account_number = random.getrandbits(64)
    owner_customer = Customer.objects.get(pk=customer_foreign_key)
    if owner_customer:
        new_customer_account = Account.create(random_account_number, False, owner_customer)
        return new_customer_account
    return "Customer couldn't be found."

User.add_to_class("create_customer_account", create_customer_account)

# create the Bank User, Bank Customer, Bank Accounts
# only ran at initial setup or deployment
def create_bank():
    # check if the bank is already created
    if User.objects.filter(username="BANK").exists():
        return "Bank already exists."
    with transaction.atomic():
        bank_user = User.create_user("BANK", "BANK@email.com", "BANK_NAME", "BANK_SURNAME")
        User.create_customer("BANK_USERNAME", "BANK_PASSWORD", "BANK_FN", "BANK_LN", "BANK_ADDRESS", "BANK_PHONE_NR", "gold", bank_user.id)
        bank_customer_retrieved = Customer.objects.get(username="BANK_USERNAME")
        User.create_customer_account(bank_customer_retrieved.id)
        User.create_customer_account(bank_customer_retrieved.id)
        bank_accounts_retrieved = Account.objects.all()
        Ledger.create(bank_accounts_retrieved[0], 100000.00, "Initial deposit.")
        Ledger.create(bank_accounts_retrieved[1], 999999.00, "Initial deposit.")

User.add_to_class("create_bank", create_bank)

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
        return f"{self.id} - {self.username} - {self.password} - {self.first_name} {self.last_name} - {self.address} - {self.phone_number} - {self.rank} - {self.user}"

    # retrieves all customer's accounts and accounts' movements
    def get_customer_movements(foreign_key):
        # get all customer accounts
        customer_accounts = Account.objects.filter(customer_fk_id=foreign_key)
        # get transactions those accounts made
        customer_account_movements = []
        for customer_account in customer_accounts:
            customer_account_movements.append(Ledger.objects.filter(account_id=customer_account.account_id))
        records = {
            'customer_accounts': customer_accounts,
            'customer_account_movements': customer_account_movements
        }
        return records

    # creates the loan account
    def take_loan(self, deposit_account_primary_key, amount, text):
        # get customer accounts
        available_accounts = self.get_customer_movements()["customer_accounts"]
        # check for customer rank and if the customer has available accounts for deposit
        if self.rank == 'basic':
            return "Can't make a loan. User is not of silver or gold rank."
        elif available_accounts.count() == 0:
            return "Customer doesn't have any accounts to deposit money from loan to."
        elif not available_accounts.get(account_id=deposit_account_primary_key):
            return "There is no account with such primary key that belongs to this customer."
        else:
            # find deposit account, create loan/withdrawal account, get loan account after ID is set by Django
            # then transfer money from one to another in case of error, transaction will ensure ACID
            deposit_account = Account.objects.get(pk=deposit_account_primary_key)
            with transaction.atomic():
                loan_account_account_number = Customer.create_loan_account(self).account_number
                loan_account = Account.objects.get(account_number=loan_account_account_number)
                Ledger.make_transactions(loan_account, deposit_account, amount, text)

    # pays loan to loan account/s
    # since one customer can take multiple loans, he can pay of one loan partly, one loan entirely and one loan partly or more loans entirely and one loan partly
    def pay_loan(self, account_primary_key, amount, text):
        # check if the user has loans
        loan_accounts = Account.objects.all().filter(customer_fk_id=self.id).filter(is_loan=True)
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
                return f"Paid {amount} of {total} on {loan_account.account_number} account. Need to pay {loan_account.balance} more."
            else:
                # make transaction from user account to loan account fully
                # if customer wanted to pay loan of 1000 and he is paying loan of 500, then 1000 += -500
                amount += loan_account.balance
                Ledger.make_transactions(customer_account, loan_account, -loan_account.balance, text)
                loan_account.delete()
        return

    # creates loan account and connects it to the customer
    def create_loan_account(customer_primary_key):
        random_account_number = random.getrandbits(64)
        new_loan_account = Account.create(random_account_number, True, customer_primary_key)
        return new_loan_account

# represents Account class which can belong to one Customer
class Account(models.Model):
    account_id = models.IntegerField(primary_key=True)
    account_name = models.CharField(max_length=30)
    account_number = random.getrandbits(64)
    is_loan = models.BooleanField(default=False)
    customer_fk_id = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.account_id} - {self.account_name} - {self.account_number} - {self.is_loan} - {self.customer_fk_id}"

    @classmethod
    def create(cls, account_name=account_name, account_number=account_number, is_loan=is_loan, customer_fk_id=customer_fk_id):
        new_account = cls.objects.create(
            account_name    = account_name,
            account_number  = account_number,
            is_loan         = is_loan,
            customer_fk_id  = customer_fk_id
        )
        return new_account

    # goes through Ledger table, gets all acounts with particular ID and then aggregates their amount into SUM
    @property
    def balance(self):
        return Decimal(Ledger.objects.filter(account_id=self.account_id).aggregate(Sum('amount'))['amount__sum'] or 0.00).quantize(Decimal('.00'))

# represents the Ledger class which stores transactions in a way that bulk_create() creates two rows
# one row is deduction from one account, other row is addition to other account
class Ledger(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    time_stamp = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.transaction_id} - {self.account} - {self.amount} -{self.time_stamp} - {self.text}"

    @ classmethod
    def create(cls, account=account, amount=amount, text=text):
        new_ledger_row = cls.objects.create(
            account     = account,
            amount      = amount,
            text        = text
        )
        return new_ledger_row

    # uses transaction and bulk_create to insert two rows in Ledger table
    # first row is sender account sending money, therefore amount being negative
    # second row is receiver account receiving money, therefore amount being positive
    def make_transactions(sender_account, receiver_account, amount, text):
        with transaction.atomic():
            if sender_account.balance >= amount or sender_account.is_loan == True:
                Ledger.objects.bulk_create([
                    Ledger(account=sender_account, amount=-amount, text=text),
                    Ledger(account=receiver_account, amount=amount, text=text)
                ])
            else:
                print('Transaction not allowed. Balance too low!')

