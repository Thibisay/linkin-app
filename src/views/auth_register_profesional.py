from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db import IntegrityError  # <-- IMPORTANTE: Importamos el manejador de errores de la BD
from src.forms import ProfesionalRegistrationForm

def register_profesional_view(request):
    """Registro para profesionales"""
    if request.user.is_authenticated:
        return redirect('feed_home')
    
    if request.method == 'POST':
        form = ProfesionalRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Intentamos guardar el usuario en la base de datos
                user = form.save()
                login(request, user)
                messages.success(request, _('¡Cuenta creada exitosamente! Bienvenido a Linking X.'))
                return redirect('feed_home')
                
            except IntegrityError:
                # Si la base de datos rechaza el registro (correo/usuario duplicado), atrapamos el error
                # 'email' asume que tu campo en el forms.py se llama así. Si se llama 'username', cámbialo.
                form.add_error('email', _('Este correo electrónico ya está registrado. Intenta iniciar sesión.'))
                
    else:
        form = ProfesionalRegistrationForm()
    
    return render(request, 'auth/register_profesional.html', {'form': form})