from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from src.forms import HabilidadForm, EducacionForm, ExperienciaLaboralForm
from src.models import Habilidad, Educacion, ExperienciaLaboral

@login_required
def add_section(request, section_type):
    """
    Vista para agregar una nueva sección al perfil
    """
    # Validar que el usuario sea profesional
    if request.user.tipo_usuario != 'profesional':
        messages.error(request, _('Solo profesionales pueden agregar secciones'))
        return redirect('profile_detail', user_id=request.user.id)
    
    # Determinar el formulario según el tipo de sección
    form_map = {
        'habilidad': HabilidadForm,
        'educacion': EducacionForm,
        'experiencia': ExperienciaLaboralForm,
    }
    
    if section_type not in form_map:
        messages.error(request, _('Tipo de sección inválido'))
        return redirect('profile_detail', user_id=request.user.id)
    
    FormClass = form_map[section_type]
    
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.profesional = request.user.profesional
            instance.save()
            
            messages.success(request, _('Sección agregada exitosamente'))
            return redirect('profile_detail', user_id=request.user.id)
    else:
        form = FormClass()
    
    context = {
        'form': form,
        'section': section_type,
        'action': 'add',
    }
    
    return render(request, 'profiles/add_section.html', context)


@login_required
def edit_section(request, section_type, section_id):
    """
    Vista para editar una sección existente
    """
    # Validar que el usuario sea profesional
    if request.user.tipo_usuario != 'profesional':
        messages.error(request, _('Solo profesionales pueden editar secciones'))
        return redirect('profile_detail', user_id=request.user.id)
    
    # Determinar el modelo y formulario según el tipo de sección
    model_map = {
        'habilidad': (Habilidad, HabilidadForm),
        'educacion': (Educacion, EducacionForm),
        'experiencia': (ExperienciaLaboral, ExperienciaLaboralForm),
    }
    
    if section_type not in model_map:
        messages.error(request, _('Tipo de sección inválido'))
        return redirect('profile_detail', user_id=request.user.id)
    
    Model, FormClass = model_map[section_type]
    
    # Obtener la instancia y verificar que pertenezca al usuario
    instance = get_object_or_404(
        Model,
        id=section_id,
        profesional=request.user.profesional
    )
    
    if request.method == 'POST':
        form = FormClass(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('Sección actualizada exitosamente'))
            return redirect('profile_detail', user_id=request.user.id)
    else:
        form = FormClass(instance=instance)
    
    context = {
        'form': form,
        'section': section_type,
        'action': 'edit',
        'instance': instance,
    }
    
    return render(request, 'profiles/add_section.html', context)


@login_required
def delete_section(request, section_type, section_id):
    """
    Vista para eliminar una sección
    """
    # Validar que el usuario sea profesional
    if request.user.tipo_usuario != 'profesional':
        messages.error(request, _('Solo profesionales pueden eliminar secciones'))
        return redirect('profile_detail', user_id=request.user.id)
    
    # Determinar el modelo según el tipo de sección
    model_map = {
        'habilidad': Habilidad,
        'educacion': Educacion,
        'experiencia': ExperienciaLaboral,
    }
    
    if section_type not in model_map:
        messages.error(request, _('Tipo de sección inválido'))
        return redirect('profile_detail', user_id=request.user.id)
    
    Model = model_map[section_type]
    
    # Obtener la instancia y verificar que pertenezca al usuario
    instance = get_object_or_404(
        Model,
        id=section_id,
        profesional=request.user.profesional
    )
    
    if request.method == 'POST':
        instance.delete()
        messages.success(request, _('Sección eliminada exitosamente'))
        return redirect('profile_detail', user_id=request.user.id)
    
    # Si no es POST, redirigir al perfil
    return redirect('profile_detail', user_id=request.user.id)