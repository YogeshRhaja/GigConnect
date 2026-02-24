#accounts/models.py
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('employer', 'Employer'),
        ('freelancer', 'Freelancer'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='account_profile'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
