#jobs/urls.py
from django.urls import path
from . import views

app_name = 'jobs'  # ✅ important if using namespaces

urlpatterns = [
    path('post-job/', views.post_job, name='post_job'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/view-proposals/<int:job_id>/', views.view_proposals, name='view_proposals'),
    path('employer/proposal/<int:proposal_id>/accept/', views.accept_proposal, name='accept_proposal'),
    path('employer/proposal/<int:proposal_id>/reject/', views.reject_proposal, name='reject_proposal'),
    path('invite/<int:job_id>/<int:freelancer_id>/',
         views.invite_freelancer,
         name='invite_freelancer'),
    path('invite/accept/<int:invite_id>/', views.accept_invite, name='accept_invite'),
    path('invite/decline/<int:invite_id>/', views.decline_invite, name='decline_invite'),
    path('freelancer/project/completed/<int:proposal_id>/', views.mark_project_completed,
         name='mark_project_completed'),
    path('freelancer/project/upload/<int:proposal_id>/', views.upload_submission, name='upload_submission'),
    path('freelancer/dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('project/<int:job_id>/chat/', views.job_chat, name='job_chat'),



    # ✅ this is needed
]
