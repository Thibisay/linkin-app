from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from src.models import Usuario, Profesional, Empresa
from src.forms import ProfesionalProfileForm, EmpresaProfileForm

@login_required
def profile_edit(request, user_id):
    """
    Vista de edición de perfil
    Solo el propietario puede editar su perfil
    """
    user = get_object_or_404(Usuario, id=user_id)
    
    # Verificar que sea el propietario
    if request.user.id != user_id:
        messages.error(request, _('No tienes permiso para editar este perfil'))
        return redirect('profile_detail', user_id=user_id)
    
    if user.tipo_usuario == 'profesional':
        try:
            profesional = user.profesional
        except Profesional.DoesNotExist:
            # Crear perfil si no existe
            profesional = Profesional.objects.create(
                user=user,
                cedula='',  # Deberá completarse
                fecha_nacimiento='2000-01-01'
            )
        
        if request.method == 'POST':
            form = ProfesionalProfileForm(request.POST, request.FILES, instance=profesional, user=user)
            if form.is_valid():
                # Actualizar usuario
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.ubicacion = form.cleaned_data.get('ubicacion', '')
                
                if 'foto' in request.FILES:
                    user.foto = request.FILES['foto']
                
                user.save()
                
                # Actualizar profesional
                form.save()
                
                messages.success(request, _('Perfil actualizado exitosamente'))
                return redirect('profile_detail', user_id=user_id)
        else:
            form = ProfesionalProfileForm(instance=profesional, user=user)
        
        template = 'profiles/profesional_edit.html'
    
    elif user.tipo_usuario == 'empresa':
        try:
            empresa = user.empresa
        except Empresa.DoesNotExist:
            # Crear perfil si no existe
            empresa = Empresa.objects.create(
                user=user,
                nombre_empresa=user.first_name or 'Mi Empresa',
                rif='',
                tipo_empresa='startup'
            )
        
        if request.method == 'POST':
            form = EmpresaProfileForm(request.POST, request.FILES, instance=empresa)
            if form.is_valid():
                # Actualizar usuario
                user.ubicacion = form.cleaned_data.get('ubicacion', '')
                
                if 'foto' in request.FILES:
                    user.foto = request.FILES['foto']
                
                user.save()
                
                # Actualizar empresa
                form.save()
                
                messages.success(request, _('Perfil actualizado exitosamente'))
                return redirect('profile_detail', user_id=user_id)
        else:
            form = EmpresaProfileForm(instance=empresa)
        
        template = 'profiles/empresa_edit.html'
    
    else:
        messages.error(request, _('Tipo de usuario no válido'))
        return redirect('feed_home')
    
    context = {
        'form': form,
        'profile_user': user,
    }
    
    return render(request, template, context)