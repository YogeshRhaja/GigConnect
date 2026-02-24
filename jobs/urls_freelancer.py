#urls_freelancer.py
from django.urls import path
from . import views

app_name = 'freelancer'  # ✅ matches your template

urlpatterns = [
    path('dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('apply-job/<int:job_id>/', views.apply_job, name='apply_job'),
]
