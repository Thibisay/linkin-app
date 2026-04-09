from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from src.models import OfertaEmpleo, Postulacion

@login_required
def job_apply(request, job_id):
    """
    Aplicar a una oferta de empleo
    """
    if request.user.tipo_usuario != 'profesional':
        # Si es una petición AJAX (fetch), devolvemos JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == 'POST':
            return JsonResponse({'success': False, 'error': _('Solo profesionales pueden aplicar')})
        
        messages.error(request, _('Solo profesionales pueden aplicar a ofertas'))
        return redirect('job_list')
    
    oferta = get_object_or_404(OfertaEmpleo, id=job_id, activa=True)
    
    # Verificar si ya aplicó
    if Postulacion.objects.filter(
        profesional=request.user.profesional,
        oferta=oferta
    ).exists():
        if request.method == 'POST':
            return JsonResponse({'success': False, 'error': _('Ya has aplicado a esta oferta')})
            
        messages.warning(request, _('Ya has aplicado a esta oferta'))
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        try:
            # Crear postulación
            postulacion = Postulacion.objects.create(
                profesional=request.user.profesional,
                oferta=oferta,
                habilidades_tecnicas=request.POST.get('habilidades_tecnicas', ''),
                anos_experiencia=int(request.POST.get('anos_experiencia', 0)),
                nivel_habilidad=request.POST.get('nivel_habilidad', 'junior'),
                telefono_contacto=request.POST.get('telefono_contacto', ''),
                email_contacto=request.POST.get('email_contacto', request.user.email),
                curriculum=request.FILES.get('curriculum'),
                estado='pendiente'
            )
            
            # ¡AQUÍ ESTÁ LA MAGIA! Respondemos con JSON en lugar de redirect
            return JsonResponse({'success': True})
        
        except Exception as e:
            # Si hay un error, lo enviamos en el JSON para que JS lo muestre
            return JsonResponse({'success': False, 'error': str(e)})
    
    return redirect('job_detail', job_id=job_id)

@login_required
def job_save(request, job_id):
    """
    Guardar/Desguardar una oferta
    """
    if request.user.tipo_usuario != 'profesional':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    oferta = get_object_or_404(OfertaEmpleo, id=job_id)
    
    postulacion, created = Postulacion.objects.get_or_create(
        profesional=request.user.profesional,
        oferta=oferta,
        defaults={
            'guardada': True,
            'habilidades_tecnicas': '',
            'anos_experiencia': 0,
            'nivel_habilidad': 'junior',
            'telefono_contacto': '',
            'email_contacto': request.user.email,
        }
    )
    
    if not created:
        postulacion.guardada = not postulacion.guardada
        postulacion.save()
    
    return JsonResponse({
        'success': True,
        'guardada': postulacion.guardada
    })