from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils.translation import gettext as _
from src.forms import LoginForm

def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('feed_home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, _('¡Bienvenido de nuevo!'))
                return redirect('feed_home')
            else:
                messages.error(request, _('Credenciales inválidas. Por favor, intenta de nuevo.'))
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})