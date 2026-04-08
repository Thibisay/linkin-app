from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from src.models import Profesional, Habilidad
from src.forms import HabilidadForm

@login_required
def add_skill(request, user_id):
    """Agregar habilidad al perfil profesional"""
    if request.user.id != user_id:
        messages.error(request, _('No tienes permiso'))
        return redirect('profile_detail', user_id=user_id)
    
    try:
        profesional = request.user.profesional
    except:
        messages.error(request, _('Perfil profesional no encontrado'))
        return redirect('profile_detail', user_id=user_id)
    
    if request.method == 'POST':
        form = HabilidadForm(request.POST)
        if form.is_valid():
            habilidad = form.save(commit=False)
            habilidad.profesional = profesional
            habilidad.save()
            messages.success(request, _('Habilidad agregada exitosamente'))
            return redirect('profile_detail', user_id=user_id)
    else:
        form = HabilidadForm()
    
    context = {
        'form': form,
        'action': 'add',
        'section': 'habilidades'
    }
    return render(request, 'profiles/add_section.html', context)

@login_required
def delete_skill(request, user_id, skill_id):
    """Eliminar habilidad"""
    if request.user.id != user_id:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    habilidad = get_object_or_404(Habilidad, id=skill_id, profesional__user_id=user_id)
    habilidad.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, _('Habilidad eliminada'))
    return redirect('profile_detail', user_id=user_id)