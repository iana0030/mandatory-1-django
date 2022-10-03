from random import seed, random
from django.db import models, transaction

# seed is used for random method which generates a number for Account
# BANK_FK is Bank's foreign key used to associate loan accounts with bank and make loan payments in Ledger
seed(1)
BANK_FK = 'bank_account_fk'

# represents the User class which is used by bank employees for administration or by regular customers
class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=45)
    user_email = models.CharField(max_length=45)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.id} - {self.username} - {self.user_email} - {self.first_name} - {self.last_name}"
    
    @classmethod
    def create_user(cls, username = username, user_email = user_email, first_name = first_name, last_name = last_name):
        user = cls.objects.create(
            username = username,
            user_email = user_email, 
            first_name = first_name,
            last_name = last_name
        )
        return user

    def create_customer(username, password, first_name, last_name, address, phone_number, rank, user_foreign_key):
        customer = Customer.objects.create(
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
            address = address, 
            phone_number = phone_number, 
            rank = rank,
            user_fk = User.objects.get(pk=user_foreign_key)
        )
        return customer

    def view_all_customers():
        all_customers = Customer.objects.all()
        return all_customers

    def view_all_accounts():
        all_accounts = Account.objects.all()
        return all_accounts

    def change_customer_rank(customer_primary_key, new_rank):
        customer = Customer.objects.get(pk=customer_primary_key)
        customer.rank = new_rank
        customer.save()
        return customer

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
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.username} - {self.password} - {self.first_name} {self.last_name} - {self.address} - {self.phone_number} - {self.rank}"

    # retrieves all customer's accounts and accounts' movements  
    @property
    def get_customer_movements(foreign_key):
        customer_accounts = Account.objects.all().filter('customer_fk_id'==foreign_key)
        customer_accounts_movements = Ledger.objects.all().filter('account_id'==foreign_key)
        records = [customer_accounts, customer_accounts_movements]
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

# represents Account class which can belong to one Customer
class Account(models.Model):
    account_id = models.IntegerField(primary_key=True)
    account_number = models.CharField(max_length=30)
    is_loan = models.BooleanField(default=False)
    customer_fk_id = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.account_id} - {self.account_number}"

    @classmethod
    @property
    def balance(cls):
        return float(cls.objects.all().filter('account_id'==cls.account_id).aggregate(models.Sum('amount')) or 0)

    @classmethod
    def create_customer_account(cls, customer_foreign_key):
        random_account_number = random()*10
        type(cls).objects.create(random_account_number, False , customer_foreign_key)

    @classmethod
    def create_loan_account(cls, bank_account_fk):
        random_account_number = random()*10
        type(cls).objects.create(random_account_number, True, bank_account_fk)

# represents the Ledger class which stores transactions in a way that bulk_create() creates two rows
# one row is deduction from one account, other row is addition to other account 
class Ledger(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.FloatField()
    time_stamp = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.transaction_Id} - {self.account} - {self.amount} -{self.time_stamp} - {self.text}"

    def make_transactions(sender_account, receiver_account, amount, text):
        with transaction.atomic():
            if sender_account.balance >= amount:
                Ledger.objects.bulk_create([
                    Ledger(account=sender_account.account_number, amount=-amount, text=text),
                    Ledger(account=receiver_account.account_number, amount=amount, text=text)
                ])
            else:
                print('Transaction not allowed. Balance too low!')

