from django.contrib import admin
from django.contrib import admin
from .models import Wallet, EscrowTransaction

admin.site.register(Wallet)
admin.site.register(EscrowTransaction)

