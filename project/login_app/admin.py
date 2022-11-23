from django.contrib import admin
from .models import PasswordResetRequest, OTPUser


admin.site.register(PasswordResetRequest)
admin.site.register(OTPUser)
