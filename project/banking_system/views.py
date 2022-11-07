from django.shortcuts import render
from .models import User, Customer, Account, Ledger


def index(request):
    return render(request, 'banking_system/index.html', {})

# USER methods
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        new_user = User.create_user(username, email, first_name, last_name)
        return render(request, 'banking_system/index.html', {'new_user': new_user})

def create_customer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        rank = request.POST['rank']
        user_foreign_key = request.POST['user_foreign_key']

        new_customer = User.create_customer(username, password, first_name, last_name, address, phone_number, rank, user_foreign_key)
        return render(request, 'banking_system/index.html', {'new_customer': new_customer})