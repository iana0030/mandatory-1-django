from django.db import models, transaction

class Account(models.Model):
    account_id = models.IntegerField(primary_key=True)
    account_number = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.account_id} - {self.account_number}"

    @classmethod
    @property
    def balance(cls):
        return int(cls.objects.all().filter('account_id'==cls.account_id).aggregate(Sum('amount')) or 0)

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


