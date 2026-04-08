from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from src.models import Profesional, Educacion
from src.forms import EducacionForm

@login_required
def add_education(request, user_id):
    """Agregar educación al perfil profesional"""
    if request.user.id != user_id:
        messages.error(request, _('No tienes permiso'))
        return redirect('profile_detail', user_id=user_id)
    
    try:
        profesional = request.user.profesional
    except:
        messages.error(request, _('Perfil profesional no encontrado'))
        return redirect('profile_detail', user_id=user_id)
    
    if request.method == 'POST':
        form = EducacionForm(request.POST)
        if form.is_valid():
            educacion = form.save(commit=False)
            educacion.profesional = profesional
            educacion.save()
            messages.success(request, _('Educación agregada exitosamente'))
            return redirect('profile_detail', user_id=user_id)
    else:
        form = EducacionForm()
    
    context = {
        'form': form,
        'action': 'add',
        'section': 'educacion'
    }
    return render(request, 'profiles/add_section.html', context)

@login_required
def edit_education(request, user_id, education_id):
    """Editar educación"""
    if request.user.id != user_id:
        messages.error(request, _('No tienes permiso'))
        return redirect('profile_detail', user_id=user_id)
    
    educacion = get_object_or_404(Educacion, id=education_id, profesional__user_id=user_id)
    
    if request.method == 'POST':
        form = EducacionForm(request.POST, instance=educacion)
        if form.is_valid():
            form.save()
            messages.success(request, _('Educación actualizada'))
            return redirect('profile_detail', user_id=user_id)
    else:
        form = EducacionForm(instance=educacion)
    
    context = {
        'form': form,
        'action': 'edit',
        'section': 'educacion',
        'item': educacion
    }
    return render(request, 'profiles/add_section.html', context)

@login_required
def delete_education(request, user_id, education_id):
    """Eliminar educación"""
    if request.user.id != user_id:
        messages.error(request, _('No tienes permiso'))
        return redirect('profile_detail', user_id=user_id)
    
    educacion = get_object_or_404(Educacion, id=education_id, profesional__user_id=user_id)
    educacion.delete()
    messages.success(request, _('Educación eliminada'))
    return redirect('profile_detail', user_id=user_id)