from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm, CustomLoginForm, CustomProfileForm
from django.http import HttpResponseForbidden
from .models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


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
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        password_fields = ['old_password', 'new_password1', 'new_password2']
        password_data_filled = all(request.POST.get(f, '') for f in password_fields)
        changed_fields = set(form.changed_data)
        updated = []

        # Handle password change if all password fields are filled
        if password_data_filled:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                updated.append('Password')
            else:
                return render(request, 'edit_profile.html', {'form': form, 'password_form': password_form})

        # Handle profile update (username, role, etc.)
        if changed_fields:
            if form.is_valid():
                form.save()
                if 'username' in changed_fields:
                    updated.append('Username')
                if 'role' in changed_fields:
                    updated.append('Role')
                if 'email' in changed_fields:
                    updated.append('Email')
            else:
                return render(request, 'edit_profile.html', {'form': form, 'password_form': password_form})

        if updated:
            messages.success(request, f"{' / '.join(updated)} updated successfully!")
            return redirect('edit_profile')
        else:
            messages.info(request, 'No changes detected.')
            return redirect('edit_profile')
    else:
        form = CustomProfileForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)
    return render(request, 'edit_profile.html', {'form': form, 'password_form': password_form})
