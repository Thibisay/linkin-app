from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from src.models import Profesional, ExperienciaLaboral
from src.forms import ExperienciaLaboralForm

@login_required
def add_experience(request, user_id):
    """Agregar experiencia laboral"""
    if request.user.id != user_id:
        messages.error(request, _('No tienes permiso'))
        return redirect('profile_detail', user_id=user_id)
    
    try:
        profesional = request.user.profesional
    except:
        messages.error(request, _('Perfil profesional no encontrado'))
        return redirect('profile_detail', user_id=user_id)
    
    if request.method == 'POST':
        form = ExperienciaLaboralForm(request.POST)
        if form.is_valid():
            experiencia = form.save(commit=False)
            experiencia.profesional = profesional
            experiencia.save()
            messages.success(request, _('Experiencia agregada exitosamente'))
            return redirect('profile_detail', user_id=user_id)
    else:
        form = ExperienciaLaboralForm()
    
    context = {
        'form': form,
        'action': 'add',
        'section': 'experiencia'
    }
    return render(request, 'profiles/add_section.html', context)

@login_required
def edit_experience(request, user_id, experience_id):
    """Editar experiencia laboral"""
    if request.user.id != user_id:
        messages.error(request, _('No tienes permiso'))
        return redirect('profile_detail', user_id=user_id)
    
    experiencia = get_object_or_404(ExperienciaLaboral, id=experience_id, profesional__user_id=user_id)
    
    if request.method == 'POST':
        form = ExperienciaLaboralForm(request.POST, instance=experiencia)
        if form.is_valid():
            form.save()
            messages.success(request, _('Experiencia actualizada'))
            return redirect('profile_detail', user_id=user_id)
    else:
        form = ExperienciaLaboralForm(instance=experiencia)
    
    context = {
        'form': form,
        'action': 'edit',
        'section': 'experiencia',
        'item': experiencia
    }
    return render(request, 'profiles/add_section.html', context)

@login_required
def delete_experience(request, user_id, experience_id):
    """Eliminar experiencia laboral"""
    if request.user.id != user_id:
        messages.error(request, _('No tienes permiso'))
        return redirect('profile_detail', user_id=user_id)
    
    experiencia = get_object_or_404(ExperienciaLaboral, id=experience_id, profesional__user_id=user_id)
    experiencia.delete()
    messages.success(request, _('Experiencia eliminada'))
    return redirect('profile_detail', user_id=user_id)