from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm, CustomLoginForm
from django.http import HttpResponseForbidden
from .models import CustomUser

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    role = request.user.role

    if role == 'admin':
        return render(request, 'users/admin_dashboard.html')
    elif role == 'manager':
        return render(request, 'users/manager_dashboard.html')
    elif role == 'staff':
        return render(request, 'users/staff_dashboard.html')
    elif role == 'supplier':
        return render(request, 'users/supplier_dashboard.html')
    else:
        return HttpResponseForbidden("Unknown role. Access denied.")
