from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext as _
from src.forms import EmpresaRegistrationForm

def register_empresa_view(request):
    """Registro para empresas"""
    if request.user.is_authenticated:
        return redirect('feed_home')
    
    if request.method == 'POST':
        form = EmpresaRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('¡Empresa registrada exitosamente! Bienvenido a Linking X.'))
            return redirect('feed_home')
    else:
        form = EmpresaRegistrationForm()
    
    return render(request, 'auth/register_empresa.html', {'form': form})