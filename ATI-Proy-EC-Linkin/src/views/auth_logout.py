from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.translation import gettext as _

def logout_view(request):
    logout(request)
    messages.info(request, _('Has cerrado sesión correctamente.'))
    return redirect('auth_login') # Redirige al nombre de la nueva URL