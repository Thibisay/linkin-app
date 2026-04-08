from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.db.models import Q, Count
from src.models import OfertaEmpleo, Postulacion

@login_required
def job_applicants(request, job_id):
    """
    Vista de postulantes para una oferta de empleo (solo empresas)
    """
    # Verificar que el usuario sea empresa
    if request.user.tipo_usuario != 'empresa':
        messages.error(request, _('No tienes permiso para ver esta página'))
        return redirect('job_detail', job_id=job_id)
    
    # Obtener la oferta y verificar que pertenezca a la empresa
    oferta = get_object_or_404(
        OfertaEmpleo,
        id=job_id,
        empresa=request.user.empresa
    )
    
    # Obtener todas las postulaciones
    postulaciones = Postulacion.objects.filter(
        oferta=oferta
    ).select_related(
        'profesional__user'
    ).order_by('-fecha_postulacion')
    
    # Filtrar por estado
    postulaciones_pendientes = postulaciones.filter(estado='pendiente')
    postulaciones_aceptadas = postulaciones.filter(estado='aceptada')
    postulaciones_rechazadas = postulaciones.filter(estado='rechazada')
    
    # Otras ofertas de la empresa
    otras_ofertas = OfertaEmpleo.objects.filter(
        empresa=request.user.empresa,
        activa=True
    ).exclude(id=job_id).annotate(
        postulaciones_count=Count('postulaciones')
    )[:5]
    
    context = {
        'oferta': oferta,
        'postulaciones': postulaciones,
        'postulaciones_pendientes': postulaciones_pendientes,
        'postulaciones_aceptadas': postulaciones_aceptadas,
        'postulaciones_rechazadas': postulaciones_rechazadas,
        'otras_ofertas': otras_ofertas,
    }
    
    return render(request, 'jobs/job_applicants.html', context)


@login_required
def update_application_status(request, application_id):
    """
    API para actualizar el estado de una postulación
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    # Verificar que el usuario sea empresa
    if request.user.tipo_usuario != 'empresa':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    import json
    data = json.loads(request.body)
    nuevo_estado = data.get('estado')
    
    # Validar estado
    if nuevo_estado not in ['aceptada', 'rechazada', 'en_revision', 'entrevista']:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    
    # Obtener postulación y verificar permisos
    postulacion = get_object_or_404(
        Postulacion,
        id=application_id,
        oferta__empresa=request.user.empresa
    )
    
    # Actualizar estado
    postulacion.estado = nuevo_estado
    postulacion.save()
    
    return JsonResponse({
        'success': True,
        'message': _('Estado actualizado correctamente'),
        'new_status': nuevo_estado
    })