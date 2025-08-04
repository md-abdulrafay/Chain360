from functools import wraps
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Supplier

def supplier_required(view_func):
    """
    Decorator that ensures the user is a supplier
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role != 'supplier':
            # Stay on the current page and show error instead of redirecting
            context = {
                'error_title': 'Access Denied',
                'error_message': 'This page is only accessible to suppliers.',
                'user_role': request.user.role,
                'suggested_action': 'As a staff member, you can manage purchase orders from the staff dashboard.' if request.user.role in ['staff', 'admin'] else 'Please contact an administrator for access.',
                'dashboard_url': '/purchases/' if request.user.role in ['staff', 'admin'] else '/dashboard/',
                'dashboard_text': 'Go to Purchase Management' if request.user.role in ['staff', 'admin'] else 'Go to Dashboard'
            }
            return render(request, 'error_pages/access_denied.html', context, status=403)
        
        # For suppliers, check if their supplier record exists
        try:
            from suppliers.models import Supplier
            supplier = Supplier.objects.get(user=request.user)
            # Add supplier to request for easy access in views
            request.supplier = supplier
        except Supplier.DoesNotExist:
            context = {
                'error_title': 'Supplier Profile Missing',
                'error_message': 'No supplier record found for your account.',
                'user_role': request.user.role,
                'suggested_action': 'Please contact administration to set up your supplier profile.',
                'dashboard_url': '/dashboard/',
                'dashboard_text': 'Go to Dashboard'
            }
            return render(request, 'error_pages/access_denied.html', context, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def staff_or_admin_required(view_func):
    """
    Decorator that ensures the user is staff or admin
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role not in ['staff', 'admin']:
            # Stay on the current page and show error instead of redirecting
            context = {
                'error_title': 'Access Denied',
                'error_message': 'This page is only accessible to staff and administrators.',
                'user_role': request.user.role,
                'suggested_action': 'As a supplier, you can view your purchase orders from your dashboard.' if request.user.role == 'supplier' else 'Please contact an administrator for access.',
                'dashboard_url': '/purchases/supplier/' if request.user.role == 'supplier' else '/dashboard/',
                'dashboard_text': 'Go to Supplier Dashboard' if request.user.role == 'supplier' else 'Go to Dashboard'
            }
            return render(request, 'error_pages/access_denied.html', context, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
