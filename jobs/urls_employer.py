#urls_employer.py
from django.urls import path
from . import views

app_name = 'employer'  # ✅ matches your template

urlpatterns = [
    path('dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('post-job/', views.post_job, name='post_job'),
    path('view-proposals/<int:job_id>/', views.view_proposals, name='view_proposals'),
]
