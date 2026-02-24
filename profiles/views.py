from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import FreelancerSkill

@login_required
def edit_skills(request):
    # Only freelancers
    if not hasattr(request.user, 'account_profile') or request.user.account_profile.role != 'freelancer':
        return redirect('/')  # or some "access denied" page

    # Get existing skills or create new
    skill_obj, created = FreelancerSkill.objects.get_or_create(freelancer=request.user)

    if request.method == 'POST':
        skills_text = request.POST.get('skills', '')
        skill_obj.skills = skills_text
        skill_obj.save()
        return redirect('profiles:edit_skills')  # stay on same page after save

    return render(request, 'profile/edit_skills.html', {
        'skill_obj': skill_obj
    })
