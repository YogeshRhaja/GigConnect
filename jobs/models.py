#jobs/model.py
from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE)

    # ✅ ADD THIS FIELD
    freelancer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_jobs'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    skills_required = models.TextField()
    budget = models.FloatField()
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Proposal(models.Model):

    STATUS_CHOICES = [
        ('pending','Pending'),
        ('accepted','Accepted'),
        ('rejected','Rejected'),
        ('completed','Completed'),   # ✅ ADD THIS
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.FloatField()
    cover_letter = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    submission = models.FileField(upload_to='submissions/', null=True, blank=True)

class JobInvite(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )

    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invites')

    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.title} → {self.freelancer.username}"

class ProjectChat(models.Model):
    job = models.OneToOneField('Job', on_delete=models.CASCADE, related_name='chat')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat for {self.job.title}"

class Message(models.Model):
    chat = models.ForeignKey(ProjectChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
