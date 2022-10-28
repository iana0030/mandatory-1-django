from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum
import random

# BANK_FK is Bank's foreign key used to associate loan accounts with bank and make loan payments in Ledger
BANK_FK = 'bank_account_fk'

# after every defined method, that method with the same name is added to Django's User class via User.add_to_class method

# represents the User class which is used by bank employees for administration or by regular customers
def __str__(self):
    return f"{self.id} - {self.username} - {self.email} - {self.first_name} - {self.last_name}"
    
User.add_to_class("__str__", __str__)

# method for creating the user
def create_user(username, email, first_name, last_name):
    user = User.objects.create(
        username = username,
        email = email, 
        first_name = first_name,
        last_name = last_name
    )
    return user

User.add_to_class("create_user", create_user)

# pass all the arguments for creating the customer and user_foreign_key to connect the customer with the user 
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

# method for creating the Bank User, Bank Customer, Bank Accounts 
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
        return f"\n{self.id} - {self.username} - {self.password} - {self.first_name} {self.last_name} - {self.address} - {self.phone_number} - {self.rank} - {self.user}"

    # retrieves all customer's accounts and accounts' movements  
    def get_customer_movements(foreign_key):
        # get all customer accounts
        customer_accounts = Account.objects.filter(customer_fk_id=foreign_key)
        # get transactions those accounts made
        customer_account_movements = []
        for customer_account in customer_accounts:
            customer_account_movements.append(Ledger.objects.filter(account_id=customer_account.account_id))
        records = [customer_accounts, customer_account_movements]
        return records
        
    # creates the loan account 
    def take_loan(self, amount, text):
        if not self.rank == 'silver' or self.rank == 'gold':
            return "Can't make a loan. User is of basic rank."
        elif Customer.get_customer_movements == 0:
            return "Can't make a loan. User has no accounts to deposit money."
        else:
            bank_account = Account.create_loan_account(Account, BANK_FK) 
            Ledger.make_transactions(bank_account, self, amount, text)
    
    # creates the transaction to loan account
    def pay_loan(self, amount, text):
        if not self.rank == 'silver' or self.rank == 'gold':
            return "Can't pay a loan. User is of basic rank."
        elif Customer.get_customer_movements == 0:
            return "Can't pay a loan. User has no accounts to pay from."
        else:
            Ledger.make_transactions(self, BANK_FK, amount, text)

    def create_loan_account(bank_account_fk):
        random_account_number = random()*10
        Account.create_account(Account, True, bank_account_fk)

# represents Account class which can belong to one Customer
class Account(models.Model):
    account_id = models.IntegerField(primary_key=True)
    account_number = models.CharField(max_length=30)
    is_loan = models.BooleanField(default=False)
    customer_fk_id = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.account_id} - {self.account_number} - {self.is_loan} - {self.customer_fk_id}"

    @classmethod
    def create(cls, account_number=account_number, is_loan=is_loan, customer_fk_id=customer_fk_id):
        new_account = cls.objects.create(
            account_number  = account_number,
            is_loan         = is_loan,
            customer_fk_id  = customer_fk_id
        )
        return new_account

    @property
    def balance(self):
        print(self)
        # return float(cls.objects.filter('account_id'==cls.account_id).aggregate(models.Sum('amount')) or 0.00)
        # return float (cls.objects.filter(ledger__account_id=cls.account_id).aggregate(models.Sum('amount')) or 0.00)
        return float(Ledger.objects.filter(account_id=self.account_id).aggregate(Sum('amount'))['amount__sum'] or 0.00)

# represents the Ledger class which stores transactions in a way that bulk_create() creates two rows
# one row is deduction from one account, other row is addition to other account 
class Ledger(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.FloatField()
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

    def make_transactions(sender_account, receiver_account, amount, text):
        with transaction.atomic():
            if sender_account.balance >= amount:
                Ledger.objects.bulk_create([
                    Ledger(account_id=sender_account.account_id, amount=-amount, text=text),
                    Ledger(account_id=receiver_account.account_id, amount=amount, text=text)
                    # Ledger(account=sender_account.account_number, amount=-amount, text=text),
                    # Ledger(account=receiver_account.account_number, amount=amount, text=text)
                ])
            else:
                print('Transaction not allowed. Balance too low!')

