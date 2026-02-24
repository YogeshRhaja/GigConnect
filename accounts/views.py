# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile  # only this, no FreelancerProfile

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        # 1️⃣ Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 2️⃣ Create UserProfile with role
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )

        # 3️⃣ Log in the user
        login(request, user)
        return redirect('accounts:redirect_after_login')

    return render(request, 'accounts/signup.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('accounts:redirect_after_login')  # role-based redirect
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def redirect_after_login(request):
    # get user profile safely
    profile = getattr(request.user, 'account_profile', None)

    if not profile:
        messages.error(request, "No profile found for this user.")
        return redirect('accounts:login')

    if profile.role == 'employer':
        return redirect('employer:employer_dashboard')
    elif profile.role == 'freelancer':
        return redirect('freelancer:freelancer_dashboard')

    return redirect('home')

def home(request):
    if request.user.is_authenticated:
        role = request.user.account_profile.role
        if role == "freelancer":
            return redirect("freelancer:freelancer_dashboard")
        else:
            return redirect("employer:employer_dashboard")
    return render(request, "home.html")
