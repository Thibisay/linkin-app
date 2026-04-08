from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

def register_role_view(request):
    """Vista de selección de rol antes del registro"""
    if request.user.is_authenticated:
        return redirect('feed_home')
    
    return render(request, 'auth/register_role.html')