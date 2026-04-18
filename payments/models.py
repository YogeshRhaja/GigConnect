from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

class EscrowTransaction(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE)
    employer = models.ForeignKey(User, related_name='employer', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, related_name='freelancer', on_delete=models.CASCADE)
    amount = models.FloatField()
    released = models.BooleanField(default=False)
@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
from django.db import models

# Create your models here.
