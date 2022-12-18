from django.shortcuts import render, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from . models import PasswordResetRequest, OTPUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import pyotp, qrcode, os.path, base64
from os import path


def verify_token(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {
            'user': user,
            'pk': pk
            }

    # Return the verification form
    if request.method == 'GET':
        context = {
                'user': user
                }

        return render(request, 'login_app/verify_token.html', context)


    # Authentication of user input
    if request.method == "POST":
        pk = request.POST["pk"]

        # Get the user's otp and encode it
        user_otp = OTPUser.objects.get(user_id=user.id).secret_otp
        secret = user_otp.encode()

        # Get the authentication number
        totp = pyotp.TOTP(secret)
        t = totp.now()

        # Verify that the number the user is entering is correct
        totp_token = request.POST["totp_token"]
        if totp.verify(totp_token) == True:
            print("TOTP matches")
            dj_login(request, user)
            return HttpResponseRedirect(reverse('banking_system:index'))
        elif totp.verify(totp_token) == False:
            print("TOTP doesn't match")
            print(totp_token)
            context = {
                    'error': "The token doesn't match, Please try again."
                    }
        else:
            context = {
                    'error': 'Bad username or password.'
                    }

    return render(request, 'login_app/login.html', context)


def login(request):
    context = {}

    if request.method == "POST":
        user = authenticate(request, username=request.POST['user'], password=request.POST['password'])

        # In case username or password is wrong and authenticate can't find user
        if not user:
            return render(request, 'login_app/sign_up.html')

        context = {
                'user': user
                }

        # Values to insert in the provisioning uri for authenticator app
        issuer_name = "BANK CO."
        secret = pyotp.random_base32()

        # Checks if the user has a secret_otp value and creates it if they don't
        if not OTPUser.objects.filter(user_id=user.id):
            print("NO OTP")
            secret = pyotp.random_base32()
            OTPUser.create(user=user, secret_otp=secret)

        # If user logs in for the first time they will get an auth uri and a qrcode generated
        if user.last_login == None:
            print("User hasn't logged in before")
            user_otp = OTPUser.objects.get(user_id=user.id).secret_otp
            key_str = pyotp.TOTP(user_otp).provisioning_uri(name=user.username, issuer_name=issuer_name)
            qr_img = qrcode.make(key_str)

            # Checks if the qrcode is saved as an image and creates it if not
            if path.exists(f'./media/{user_otp}.jpg'):
                print("The file already exists")
            else:
                print("The file doesn't exist yet. Creating file....'")
                qr_img.save(f'./media/{user_otp}.jpg')

            context = {
                    'qr_img': qr_img,
                    'user_otp': user_otp,
                    'user': user
                    }

            return render(request, 'login_app/login-token.html', context)
        elif user:
            issuer_name = "BANK CO."
            user_otp = OTPUser.objects.get(user_id=user.id).secret_otp
            key_str = pyotp.TOTP(user_otp).provisioning_uri(name=user.username, issuer_name=issuer_name)
            qr_img = qrcode.make(key_str)

            # Checks if the qrcode is saved as an image creates it if not
            if path.exists(f'./media/{user_otp}.jpg'):
                print("The file already exists")
            else:
                print("The file doesn't exist yet. Creating file....'")
                qr_img.save(f'./media/{user_otp}.jpg')

            context = {
                    'user_otp': user_otp,
                    'user': user
                    }

            return render(request, 'login_app/login-token.html', context)
        else:
            context = {
                    'error': 'Bad username or password.'
                    }

    return render(request, 'login_app/login.html', context)


def logout(request):
    dj_logout(request)
    return render(request, 'login_app/login.html')


def request_password_reset(request):
    if request.method == "POST":
        post_user = request.POST['username']
        user = None

        if post_user:
            try:
                user = User.objects.get(username=post_user)
            except:
                print(f"Invalid password request: {post_user}")
        else:
            post_user = request.POST['email']
            try:
                user = User.objects.get(email=post_user)
            except:
                print(f"Invalid password request: {post_user}")
        if user:
            prr = PasswordResetRequest()
            prr.user = user
            prr.save()
            print(prr)
            return HttpResponseRedirect(reverse('login_app:password_reset'))

    return render(request, 'login_app/request_password_reset.html')

def password_reset(request):
    if request.method == "POST":
        post_user = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        token = request.POST['token']

        if password == confirm_password:
            try:
                prr = PasswordResetRequest.objects.get(token=token)
                prr.save()
            except:
                print("Invalid password reset attempt")
                return render(request, 'login_app/password_reset.html')

            user = prr.user
            user.set_password(password)
            user.save()
            return HttpResponseRedirect(reverse('login_app:login'))

    return render(request, 'login_app/password_reset.html')


def sign_up(request):
    context = {}
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_name = request.POST['user']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        if password == confirm_password:
            if User.objects.create_user(user_name, first_name=first_name, last_name=last_name, email=email, password=password):
                return HttpResponseRedirect(reverse('login_app:login'))
            else:
                context = {
                        'error': 'Could not create user account - please try again.'
                        }
        else:
            context = {
                    'error': 'Passwords did not match. Please try again.'
                    }

    return render(request, 'login_app/sign_up.html', context)



@login_required
def delete_account(request):
    if request.method == "POST":
        if request.POST['confirm_deletion'] == "DELETE":
            user = authenticate(request, username=request.user.username, password=request.POST['password'])
            if user:
                print(f"Deleting user {user}")
                user.delete()
                return HttpResponseRedirect(reverse('login_app:login'))
            else:
                print("Delete failed")

    return render(request, 'login_app/delete_account.html')

