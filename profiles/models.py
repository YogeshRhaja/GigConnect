from django.db import models
from django.contrib.auth.models import User

class FreelancerSkill(models.Model):
    freelancer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='skills_profile'
    )
    skills = models.TextField(
        help_text="Comma separated skills like Python, Django, ML"
    )

    def __str__(self):
        return self.freelancer.username
