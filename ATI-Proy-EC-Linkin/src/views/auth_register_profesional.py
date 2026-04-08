from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext as _
from src.forms import ProfesionalRegistrationForm

def register_profesional_view(request):
    """Registro para profesionales"""
    if request.user.is_authenticated:
        return redirect('feed_home')
    
    if request.method == 'POST':
        form = ProfesionalRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('¡Cuenta creada exitosamente! Bienvenido a Linking X.'))
            return redirect('feed_home')
    else:
        form = ProfesionalRegistrationForm()
    
    return render(request, 'auth/register_profesional.html', {'form': form})