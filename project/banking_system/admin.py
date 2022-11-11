from django.contrib import admin
from .models import User, Customer, Ledger, Account

admin.site.register(Customer)
admin.site.register(Ledger)
admin.site.register(Account)


# Register your models here.
