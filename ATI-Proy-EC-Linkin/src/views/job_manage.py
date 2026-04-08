from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from src.forms import OfertaEmpleoForm
from src.models import OfertaEmpleo

@login_required
def create_job(request):
    """
    Vista para crear una nueva oferta de empleo
    """
    # Verificar que el usuario sea empresa
    if request.user.tipo_usuario != 'empresa':
        messages.error(request, _('Solo empresas pueden crear ofertas de empleo'))
        return redirect('job_list')
    
    if request.method == 'POST':
        form = OfertaEmpleoForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.empresa = request.user.empresa
            oferta.activa = True
            oferta.save()
            
            messages.success(request, _('Oferta de empleo creada exitosamente'))
            return redirect('job_detail', job_id=oferta.id)
    else:
        form = OfertaEmpleoForm()
    
    context = {
        'form': form,
        'action': 'create',
    }
    
    return render(request, 'jobs/job_form.html', context)


@login_required
def edit_job(request, job_id):
    """
    Vista para editar una oferta de empleo existente
    """
    # Verificar que el usuario sea empresa
    if request.user.tipo_usuario != 'empresa':
        messages.error(request, _('No tienes permiso para editar ofertas'))
        return redirect('job_detail', job_id=job_id)
    
    # Obtener la oferta y verificar que pertenezca a la empresa
    oferta = get_object_or_404(
        OfertaEmpleo,
        id=job_id,
        empresa=request.user.empresa
    )
    
    if request.method == 'POST':
        form = OfertaEmpleoForm(request.POST, instance=oferta)
        if form.is_valid():
            form.save()
            messages.success(request, _('Oferta actualizada exitosamente'))
            return redirect('job_detail', job_id=oferta.id)
    else:
        form = OfertaEmpleoForm(instance=oferta)
    
    context = {
        'form': form,
        'oferta': oferta,
        'action': 'edit',
    }
    
    return render(request, 'jobs/job_form.html', context)


@login_required
def toggle_job_status(request, job_id):
    """
    Vista para activar/desactivar una oferta de empleo
    """
    if request.method != 'POST':
        return redirect('job_list')
    
    # Verificar que el usuario sea empresa
    if request.user.tipo_usuario != 'empresa':
        messages.error(request, _('No tienes permiso'))
        return redirect('job_list')
    
    # Obtener la oferta y verificar que pertenezca a la empresa
    oferta = get_object_or_404(
        OfertaEmpleo,
        id=job_id,
        empresa=request.user.empresa
    )
    
    # Toggle status
    oferta.activa = not oferta.activa
    oferta.save()
    
    if oferta.activa:
        messages.success(request, _('Oferta activada exitosamente'))
    else:
        messages.success(request, _('Oferta pausada exitosamente'))
    
    # Redirigir a la lista de ofertas en lugar de detail
    return redirect('job_list')


@login_required
def delete_job(request, job_id):
    """
    Vista para eliminar una oferta de empleo
    """
    if request.method != 'POST':
        return redirect('job_list')
    
    # Verificar que el usuario sea empresa
    if request.user.tipo_usuario != 'empresa':
        messages.error(request, _('No tienes permiso'))
        return redirect('job_list')
    
    # Obtener la oferta y verificar que pertenezca a la empresa
    oferta = get_object_or_404(
        OfertaEmpleo,
        id=job_id,
        empresa=request.user.empresa
    )
    
    oferta.delete()
    messages.success(request, _('Oferta eliminada exitosamente'))
    
    return redirect('job_list')