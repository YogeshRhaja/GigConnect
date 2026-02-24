from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

class EscrowTransaction(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE)
    employer = models.ForeignKey(User, related_name='employer', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, related_name='freelancer', on_delete=models.CASCADE)
    amount = models.FloatField()
    released = models.BooleanField(default=False)
from django.db import models

# Create your models here.
