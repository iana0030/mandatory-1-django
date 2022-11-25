from django.db import models
from django.contrib.auth.models import User
from secrets import token_urlsafe

class OTPUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_otp = models.CharField(max_length=16)

    def __str__(self):
        return f'{self.user} - {self.secret_otp}'


    @classmethod
    def create(cls, user, secret_otp):
        cls.objects.create(
                user=user,
                secret_otp=secret_otp
                )


class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=43, default=token_urlsafe)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    updated_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.created_timestamp} - {self.updated_timestamp} - {self.token}'
