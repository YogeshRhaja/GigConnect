from django.urls import path
from .views import edit_skills

app_name = 'profiles'

urlpatterns = [
    path('skills/', edit_skills, name='edit_skills'),
]
