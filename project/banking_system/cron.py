from .models import Account, Ledger
from django.db.models import F, Value
from django.db.models.functions import Concat

def interest_cronjob():
    # When loan balance is less than zero, it is a loan account with a borrowed amount
    # The cronjob will run every 5 minutes adding interest to the balance
    # The interest is 2% so if customer borrows 500
    # The amount they will pay back 500 plus the interest which would be 510
    # When account balance reaches 0 and everything is paid back the cronjob doesn't do anything
    Ledger.objects.all()
    Ledger.objects.filter(amount__lt=0).update(amount=F('amount')/100*2+F('amount'))
    Ledger.objects.all()

    # Just appending some text to existing text, showcasing that interest has been added
    if not Ledger.objects.filter(amount__lt=0, text__contains='Added 2% interest'):
        Ledger.objects.filter(amount__lt=0).update(text=Concat('text', Value(' - Added 2% interest')))

