# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email    = request.POST['email']
        password = request.POST['password']
        role     = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'accounts/signup.html')  # ← render, not redirect (safer for messages)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )
        if not created:
            profile.role = role
            profile.save()

        login(request, user)
        return redirect('accounts:redirect_after_login')

    return render(request, 'accounts/signup.html')


def user_login(request):
    # Already logged in? skip the login page
    if request.user.is_authenticated:
        return redirect('accounts:redirect_after_login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('accounts:redirect_after_login')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'accounts/login.html')  # render directly, no redirect

    return render(request, 'accounts/login.html')



def user_logout(request):
    logout(request)
    messages.success(request, "You've been logged out successfully.")
    return redirect('home')


@login_required
def redirect_after_login(request):
    profile = getattr(request.user, 'account_profile', None)

    if not profile:
        messages.error(request, "No profile found. Please contact support.")
        return redirect('accounts:login')

    if profile.role == 'employer':
        return redirect('employer:employer_dashboard')
    elif profile.role == 'freelancer':
        return redirect('freelancer:freelancer_dashboard')

    return redirect('home')


def home(request):
    if request.user.is_authenticated:
        # Use getattr to avoid crash if profile missing
        profile = getattr(request.user, 'account_profile', None)
        if profile and profile.role == 'freelancer':
            return redirect('freelancer:freelancer_dashboard')
        elif profile:
            return redirect('employer:employer_dashboard')
    return render(request, 'home.html')