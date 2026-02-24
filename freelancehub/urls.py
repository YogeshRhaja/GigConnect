# freelancehub/urls.py
from django.contrib import admin
from django.urls import path, include
from jobs import views as job_views
from accounts import views as accounts_views
from accounts.views import home

urlpatterns = [
    path('', home, name='home'),
    path('', job_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    # redirect after login
    path('redirect-after-login/', accounts_views.redirect_after_login, name='redirect_after_login'),

    # jobs
    path('jobs/', include(('jobs.urls', 'jobs'), namespace='jobs')),
    path('employer/', include('jobs.urls_employer', namespace='employer')),
    path('freelancer/', include(('jobs.urls_freelancer', 'freelancer'), namespace='freelancer')),
    path('profile/', include('profiles.urls')),

]

