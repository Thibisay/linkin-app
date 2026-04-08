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
        messages.error(request, _('Solo profesionales pueden aplicar a ofertas'))
        return redirect('job_list')
    
    oferta = get_object_or_404(OfertaEmpleo, id=job_id, activa=True)
    
    # Verificar si ya aplicó
    if Postulacion.objects.filter(
        profesional=request.user.profesional,
        oferta=oferta
    ).exists():
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
            
            messages.success(request, _('¡Aplicación enviada exitosamente!'))
            return redirect('job_detail', job_id=job_id)
        
        except Exception as e:
            messages.error(request, _('Hubo un error al enviar tu aplicación'))
            return redirect('job_detail', job_id=job_id)
    
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