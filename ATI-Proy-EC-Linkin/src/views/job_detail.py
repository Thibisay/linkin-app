from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Q
from src.models import OfertaEmpleo, Postulacion

def job_detail(request, job_id):
    """
    Vista de detalle de una oferta de empleo
    """
    # Para empresas: permitir ver sus propias ofertas (activas o inactivas)
    # Para profesionales: solo ver ofertas activas de otras empresas
    if request.user.is_authenticated and request.user.tipo_usuario == 'empresa':
        # Empresa puede ver sus propias ofertas aunque estén inactivas
        oferta = get_object_or_404(
            OfertaEmpleo.objects.select_related('empresa__user'),
            Q(id=job_id) & (Q(activa=True) | Q(empresa=request.user.empresa))
        )
    else:
        # Profesionales solo ven ofertas activas
        oferta = get_object_or_404(
            OfertaEmpleo.objects.select_related('empresa__user'),
            id=job_id,
            activa=True
        )
    
    # Incrementar vistas solo si NO es la empresa dueña
    if not (request.user.is_authenticated and 
            request.user.tipo_usuario == 'empresa' and 
            oferta.empresa == request.user.empresa):
        oferta.vistas += 1
        oferta.save(update_fields=['vistas'])
    
    # Verificar si el usuario ya postuló
    ya_postulo = False
    guardada = False
    
    if request.user.is_authenticated and request.user.tipo_usuario == 'profesional':
        ya_postulo = Postulacion.objects.filter(
            oferta=oferta,
            profesional=request.user.profesional
        ).exists()
        
        # Verificar si está guardada
        guardada = Postulacion.objects.filter(
            oferta=oferta,
            profesional=request.user.profesional,
            guardada=True
        ).exists()
    
    # Ofertas similares (solo activas)
    ofertas_similares = OfertaEmpleo.objects.filter(
        activa=True,
        nivel=oferta.nivel
    ).exclude(
        id=oferta.id
    ).select_related('empresa__user')[:5]
    
    context = {
        'oferta': oferta,
        'ya_postulo': ya_postulo,
        'guardada': guardada,
        'ofertas_similares': ofertas_similares,
    }
    
    return render(request, 'jobs/job_detail.html', context)